#!/usr/bin/env ruby
# frozen_string_literal: true

require "yaml"
require "faraday"
require "faraday/retry"
require "faraday/multipart"
require "listen"
require "json"
require "digest"

CATEGORY_ID = ENV["DOCS_CATEGORY_ID"].to_i
DATA_EXPLORER_QUERY_ID = ENV["DOCS_DATA_EXPLORER_QUERY_ID"].to_i
DOCS_TARGET = ENV["DOCS_TARGET"]
DOCS_API_KEY = ENV["DOCS_API_KEY"]
GEMINI_API_KEY = ENV["GEMINI_API_KEY"]

VERBOSE = ARGV.include?("-v")
WATCH = ARGV.include?("--watch")
DRY_RUN = ARGV.include?("--dry-run")

require_relative "lib/local_doc"
require_relative "lib/api"
require_relative "lib/util"

# Gemini API client for title generation
class GeminiClient
#   GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
  GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"  
#   MAX_REQUESTS_PER_MINUTE = 15
  MAX_REQUESTS_PER_MINUTE = 9
  RATE_LIMIT_WINDOW = 60 # seconds

  def initialize(api_key)
    @api_key = api_key
    @request_timestamps = []
    @mutex = Mutex.new
  end

  def generate_titles(file_path, content)
    return nil unless @api_key

    wait_for_rate_limit

    prompt = build_prompt(file_path, content)
    
    response = Faraday.post(
      "#{GEMINI_API_URL}?key=#{@api_key}",
      { contents: [{ parts: [{ text: prompt }] }] }.to_json,
      "Content-Type" => "application/json"
    )

    parse_response(response)
  rescue => e
    puts "Error calling Gemini API: #{e.message}"
    nil
  end

  private

  def wait_for_rate_limit
    @mutex.synchronize do
      now = Time.now
      
      # Remove timestamps older than the rate limit window
      @request_timestamps.reject! { |ts| now - ts > RATE_LIMIT_WINDOW }
      
      # If we've hit the limit, wait until the oldest request expires
      if @request_timestamps.length >= MAX_REQUESTS_PER_MINUTE
        oldest_request = @request_timestamps.first
        sleep_time = RATE_LIMIT_WINDOW - (now - oldest_request) + 0.1 # Add small buffer
        
        if sleep_time > 0
          puts "Rate limit reached (#{MAX_REQUESTS_PER_MINUTE}/min). Waiting #{sleep_time.round(1)}s..."
          sleep(sleep_time)
          
          # Clean up again after waiting
          now = Time.now
          @request_timestamps.reject! { |ts| now - ts > RATE_LIMIT_WINDOW }
        end
      end
      
      # Record this request
      @request_timestamps << Time.now
    end
  end

  def build_prompt(file_path, content)
    <<~PROMPT
      You are helping to generate documentation metadata. Given a markdown file path and its content, generate appropriate titles.

      File path: #{file_path}
      
      Content preview:
      #{content[0..500]}

      Please analyze the file path and content, then provide:
      1. A full title (3-8 words, descriptive and professional, MUST be at least 15 characters long)
      2. A short title (1-3 words, concise, MUST be at least 15 characters long)

      CRITICAL: Both titles MUST be at least 15 characters long. If a title would be shorter, expand it with relevant context.

      Respond ONLY with valid JSON in this exact format:
      {
        "title": "Your Full Title Here",
        "short_title": "Short Title Here"
      }

      Do not include any other text, explanation, or markdown formatting.
    PROMPT
  end

  def parse_response(response)
    body = JSON.parse(response.body)
    text = body.dig("candidates", 0, "content", "parts", 0, "text")
    
    return nil unless text

    # Extract JSON from potential markdown code blocks
    json_text = text.strip.gsub(/^```json\n/, "").gsub(/\n```$/, "").strip
    
    parsed = JSON.parse(json_text)
    
    # Validate minimum length
    if parsed["title"] && parsed["title"].length < 15
      parsed["title"] = parsed["title"].ljust(15)
    end
    
    if parsed["short_title"] && parsed["short_title"].length < 15
      parsed["short_title"] = parsed["short_title"].ljust(15)
    end
    
    parsed
  rescue => e
    puts "Error parsing Gemini response: #{e.message}"
    nil
  end
end

# Helper method to convert MkDocs Material callouts to Obsidian format
def convert_mkdocs_to_obsidian_callouts(content, debug: false)
  # Map of MkDocs callout types to Obsidian equivalents
  callout_map = {
    'note' => 'note',
    'tip' => 'tip',
    'important' => 'important',
    'warning' => 'warning',
    'caution' => 'caution',
    'info' => 'info',
    'success' => 'success',
    'question' => 'question',
    'failure' => 'failure',
    'danger' => 'danger',
    'bug' => 'bug',
    'example' => 'example',
    'quote' => 'quote',
    'abstract' => 'abstract',
    'summary' => 'summary',
    'tldr' => 'tldr'
  }
  
  lines = content.lines
  result = []
  i = 0
  match_count = 0
  
  while i < lines.length
    line = lines[i]
    
    # Check if this line starts a callout
    if line =~ /^!!!\s+(#{callout_map.keys.map { |k| Regexp.escape(k) }.join('|')})(?:\s+"([^"]+)")?\s*$/
      match_count += 1
      mkdocs_type = $1
      custom_title = $2
      obsidian_type = callout_map[mkdocs_type]
      
      # Collect all indented lines that follow
      body_lines = []
      i += 1
      while i < lines.length
        current_line = lines[i]
        
        # Check if line is indented (starts with 4 spaces or tab)
        if current_line =~ /^(?:    |\t)/
          body_lines << current_line
          i += 1
        # Check if line is blank (empty or only whitespace) - might be between paragraphs
        elsif current_line =~ /^\s*$/
          # Peek ahead to see if there are more indented lines
          peek_index = i + 1
          has_more_indented = false
          while peek_index < lines.length
            if lines[peek_index] =~ /^(?:    |\t)/
              has_more_indented = true
              break
            elsif lines[peek_index] =~ /^\s*$/
              peek_index += 1
            else
              break
            end
          end
          
          if has_more_indented
            body_lines << current_line
            i += 1
          else
            break
          end
        else
          # Non-indented, non-blank line - stop here
          break
        end
      end
      
      puts "DEBUG: Match #{match_count} - type: #{mkdocs_type}, title: #{custom_title.inspect}, body lines: #{body_lines.length}" if debug
      
      # Build the converted callout
      if body_lines.empty?
        if custom_title
          result << "> [!#{obsidian_type}] \"#{custom_title}\"\n"
        else
          result << "> [!#{obsidian_type}]\n"
        end
      else
        if custom_title
          result << "> [!#{obsidian_type}] \"#{custom_title}\"\n"
        else
          result << "> [!#{obsidian_type}]\n"
        end
        # Add > prefix to each body line
        body_lines.each do |body_line|
          result << ">#{body_line}"
        end
      end
    else
      result << line
      i += 1
    end
  end
  
  puts "DEBUG: Total matches found: #{match_count}" if debug
  
  result.join
end

# Convert MkDocs Material icons to standard emojis
def convert_material_icons_to_emojis(content)
  # Map of common Material icons to emoji equivalents
  icon_map = {
    # Check/success icons
    ':material-check:' => '✅',
    ':material-check-circle:' => '✅',
    ':material-check-bold:' => '✅',
    
    # Close/error icons
    ':material-close:' => '❌',
    ':material-close-circle:' => '❌',
    ':material-alert-circle:' => '⚠️',
    
    # Info icons
    ':material-information:' => 'ℹ️',
    ':material-information-outline:' => 'ℹ️',
    ':material-help-circle:' => '❓',
    
    # Arrow icons
    ':material-arrow-right:' => '→',
    ':material-arrow-left:' => '←',
    ':material-arrow-up:' => '↑',
    ':material-arrow-down:' => '↓',
    
    # Other common icons
    ':material-lightbulb:' => '💡',
    ':material-star:' => '⭐',
    ':material-heart:' => '❤️',
    ':material-fire:' => '🔥',
    ':material-flag:' => '🚩',
    ':material-link:' => '🔗',
    ':material-pencil:' => '✏️',
    ':material-delete:' => '🗑️',
    ':material-calendar:' => '📅',
    ':material-clock:' => '🕐',
    ':material-email:' => '📧',
    ':material-phone:' => '📞',
  }
  
  # Replace material icons with emojis, ignoring any style attributes
  icon_map.each do |material_icon, emoji|
    # Match the icon with optional style attributes like { style="color: #EF5350" }
    content.gsub!(/#{Regexp.escape(material_icon)}\{\s*style="[^"]*"\s*\}/, emoji)
    # Also match without style attributes
    content.gsub!(material_icon, emoji)
  end
  
  content
end

# Helper method to generate frontmatter from file path
def generate_frontmatter_from_path(path, content = nil, gemini_client = nil)
  # Remove .md extension and get the base name
  base_name = File.basename(path, ".md")
  
  # Generate id from the full path (without extension)
  # Replace / with -
  # IMPORTANT: The LocalDoc#external_id method adds "DOC-" prefix (4 chars)
  # So we need to limit the base ID to 46 chars to stay under the 50 char API limit
  full_id = path.sub(/\.md$/, "").gsub("/", "-")
  
  # Maximum length for the base ID (50 char API limit - 4 char "DOC-" prefix)
  max_base_id_length = 46
  
  if full_id.length > max_base_id_length
    # Take first 37 chars and append an 8-char hash for uniqueness (37 + 1 dash + 8 = 46)
    hash_suffix = Digest::MD5.hexdigest(path)[0..7]
    id = "#{full_id[0..36]}-#{hash_suffix}"
  else
    id = full_id
  end
  
  # Try to use Gemini for title generation
  if gemini_client && content
    gemini_titles = gemini_client.generate_titles(path, content)
    
    if gemini_titles
      return {
        "id" => id,
        "title" => gemini_titles["title"],
        "short_title" => gemini_titles["short_title"]
      }
    end
  end
  
  # Fallback to original logic if Gemini fails or is not available
  title = base_name.split(/[-_]/).map(&:capitalize).join(" ")
  short_title = base_name.split(/[-_]/).map(&:capitalize).join(" ")
  
  # Ensure minimum length
  title = title.ljust(15) if title.length < 15
  short_title = short_title.ljust(15) if short_title.length < 15
  
  {
    "id" => id,
    "title" => title,
    "short_title" => short_title
  }
end

# Helper method to generate index.md content for a folder
def generate_folder_index(folder_name)
  # Convert folder name to a nice title (e.g., "my-folder" -> "My Folder")
  title = folder_name.split(/[-_]/).map(&:capitalize).join(" ")
  
  "---\ntitle: #{title}\n---\n"
end

# Initialize Gemini client if API key is available
gemini_client = GEMINI_API_KEY ? GeminiClient.new(GEMINI_API_KEY) : nil

if gemini_client
  puts "✓ Gemini API configured for title generation"
else
  puts "⚠ GEMINI_API_KEY not set - using fallback title generation"
end

docs = []

puts "Reading local docs..."
BASE = "#{__dir__}/../../docs_sp/"

# Generate index.md for each folder that doesn't have one
folders_needing_index = Set.new
Dir.glob("**/", base: BASE).each do |folder|
  next if folder == "./" || folder.empty?
  
  folder_path = folder.chomp("/")
  index_path = File.join(BASE, folder_path, "index.md")
  
  unless File.exist?(index_path)
    folders_needing_index.add(folder_path)
    
    # Get the folder name (last component of the path)
    folder_name = File.basename(folder_path)
    
    # Generate the index.md content
    index_content = generate_folder_index(folder_name)
    
    # Write the index.md file
    File.write(index_path, index_content)
    puts "Generated index.md for folder: #{folder_path}" if VERBOSE
  end
end

puts "Generated #{folders_needing_index.size} index.md files" if folders_needing_index.any?

Dir
  .glob("**/*.md", base: BASE)
  .each do |path|
    next if path.end_with?("index.md")
    next if path.include?("SAFETY")

    content = File.read(File.join(BASE, path))

    frontmatter, content = Util.parse_md(content)
    
    # Convert MkDocs Material callouts to Obsidian format
    content = convert_mkdocs_to_obsidian_callouts(content)
    content = convert_material_icons_to_emojis(content)

    # Generate missing frontmatter fields dynamically
    generated = generate_frontmatter_from_path(path, content, gemini_client)
    
    # Apply the generated values, ensuring ID is limited to 50 chars
    frontmatter["id"] = generated["id"]
    frontmatter["title"] ||= generated["title"]
    frontmatter["short_title"] ||= generated["short_title"]

    puts "Generated frontmatter for '#{path}': id='#{frontmatter["id"]}', title='#{frontmatter["title"]}'" if VERBOSE

    docs.push(LocalDoc.new(frontmatter:, path:, content:))
  end

puts "Validating local docs..."
docs
  .group_by { |doc| doc.external_id }
  .each do |id, docs|
    if docs.size > 1
      puts "- duplicate external_id '#{id}' found in:"
      docs.each { |doc| puts "- #{doc.path}" }
      exit 1
    end
  end

exit 0 if !DOCS_API_KEY

puts "Fetching remote info via data-explorer..."
remote_topics = API.fetch_current_state

puts "Mapping to existing topics..."
map_to_remote =
  lambda do
    docs.each do |doc|
      puts "- checking '#{doc.external_id}'..." if VERBOSE
      if topic_info = remote_topics.find { |t| t[:external_id] == doc.external_id }
        doc.topic_id = topic_info[:topic_id]
        doc.first_post_id = topic_info[:first_post_id]
        doc.remote_title = topic_info[:title]
        doc.remote_content = topic_info[:raw]
        doc.remote_deleted = topic_info[:deleted_at]
        puts "  found topic_id: #{doc.topic_id}" if VERBOSE
      else
        puts " not found" if VERBOSE
      end
    end
  end
map_to_remote.call

puts "Deleting topics if necessary..."

cat_desc_topic = remote_topics.find { |t| t[:is_index_topic] }
if cat_desc_topic.nil?
  puts "Docs category is missing an index topic"
  exit 1
end
cat_desc_topic_id = cat_desc_topic[:topic_id]

remote_topics
  .reject { |remote_doc| remote_doc[:deleted_at] }
  .reject { |remote_doc| docs.any? { |doc| doc.topic_id == remote_doc[:topic_id] } }
  .reject { |remote_doc| remote_doc[:topic_id] == cat_desc_topic_id }
  .each do |remote_doc|
    id = remote_doc[:topic_id]
    puts "- deleting topic #{id}..."
    API.trash_topic(topic_id: id)
  end

puts "Restoring topics if necessary..."
docs
  .filter(&:remote_deleted)
  .each do |doc|
    puts "- restoring '#{doc.external_id}'..."
    API.restore_topic(topic_id: doc.topic_id)
  end

puts "Creating missing topics..."
created_any = false
docs.each do |doc|
  next if doc.topic_id

  created_any = true
  puts "- creating '#{doc.external_id} with title '#{doc.frontmatter["title"]}'..."
  
  # Convert callouts before creating the topic
  converted_content = convert_mkdocs_to_obsidian_callouts(doc.content_with_uploads)
  
  API.create_topic(
    external_id: doc.external_id,
    raw: converted_content,
    category: CATEGORY_ID,
    title: doc.frontmatter["title"]
  )
rescue Faraday::UnprocessableEntityError => e
  puts " 422 error: #{e.response[:body]}"
  raise e
end

if created_any
  puts "Re-fetching remote info..."
  remote_topics = API.fetch_current_state
  map_to_remote.call
end

puts "Updating content..."
docs.each do |doc|
  if doc.topic_id.nil?
    next if DRY_RUN
    raise "Topic ID not found for '#{doc.external_id}'. Something went wrong with creating it?"
  end

  # Convert callouts in the content before comparison and upload
  converted_content = convert_mkdocs_to_obsidian_callouts(doc.content_with_uploads)

  if converted_content.strip == doc.remote_content.strip &&
       doc.frontmatter["title"] == doc.remote_title
    puts "- no changes required for '#{doc.external_id}' (topic_id: #{doc.topic_id})" if VERBOSE
    next
  end

  puts "- updating '#{doc.external_id}' (topic_id: #{doc.topic_id})..."
  API.edit_post(
    post_id: doc.first_post_id,
    raw: converted_content,
    title: doc.frontmatter["title"],
    category: CATEGORY_ID
  )
rescue Faraday::UnprocessableEntityError => e
  puts " 422 error: #{e.response[:body]}"
  raise e
end

puts "Building index..."
_, index_content = Util.parse_md(File.read("#{BASE}index.md"))
index_content += "\n\n"
docs
  .group_by { |doc| doc.section }
  .each do |section, section_docs|
    if section
      section_frontmatter, _ = Util.parse_md(File.read("#{BASE}#{section}/index.md"))
      index_content += "## #{section_frontmatter["title"]}\n\n"
    end

    section_docs.each do |doc|
      index_content +=
        "- #{doc.frontmatter["short_title"]}: [#{doc.frontmatter["title"]}](/t/-/#{doc.topic_id}?silent=true)\n"
    end
    index_content += "\n"
  end

index_post_info = remote_topics.find { |t| t[:topic_id] == cat_desc_topic_id }

if index_post_info[:raw].strip == index_content.strip
  puts "- no changes required for index"
else
  puts "- updating index..."
  API.edit_post(post_id: index_post_info[:first_post_id], raw: index_content)
end

if WATCH
  puts "Watching for changes to files..."

  Listen
    .to("#{__dir__}/docs") do |modified, added, removed|
      if added.size > 0 || removed.size > 0
        puts "Files added/removed. Restarting sync..."
        exec("ruby", "#{__dir__}/sync_docs", *ARGV)
      end

      modified.each do |path|
        relative = path.sub(BASE, "")
        doc = docs.find { |d| d.path == relative }
        raise "Modified file not recognized: #{relative}" if doc.nil?

        print "- updating '#{doc.external_id}' (topic_id: #{doc.topic_id})..."
        new_frontmatter, new_content = Util.parse_md(File.read(path))
        if %w[id short_title].any? { |key| doc.frontmatter[key] != new_frontmatter[key] }
          puts "Frontmatter changed. Restarting sync..."
          exec("ruby", "#{__dir__}/sync_docs", *ARGV)
        end
        doc.content, doc.frontmatter = new_content, new_frontmatter

        # Convert callouts before uploading
        converted_content = convert_mkdocs_to_obsidian_callouts(doc.content_with_uploads)

        API.edit_post(
          post_id: doc.first_post_id,
          raw: converted_content,
          title: doc.frontmatter["title"]
        )
        puts " done"
      end
    end
    .start

  sleep
else
  puts "Done."
end