#include "raylib.h"
#include "system/ui/raylib/util.h"
#include <string>
#include <vector>
#include <fstream>
#include <iostream>

// Function to load text from a file or default file
std::vector<std::string> LoadTextFromFile(const char* filename = nullptr) {
    std::vector<std::string> lines;
    std::string filePath = (filename != nullptr) ? filename : "/data/openpilot/tsk/ext.txt";
    std::ifstream file(filePath);
    std::string line;

    if (file.is_open()) {
        while (std::getline(file, line)) {
            lines.push_back(line);
        }
        file.close();
    } else {
        // Add error message to lines vector
        lines.push_back("Failed to open file: " + filePath);
    }

    return lines;
}

// Function to wrap text to a given width
std::vector<std::string> WrapText(Font font, const std::string& text, float fontSize, float spacing, float wrapWidth) {
    std::vector<std::string> wrappedLines;
    std::string currentLine;
    float lineWidth = 0.0f;

    for (char c : text) {
        float charWidth = MeasureTextEx(font, &c, fontSize, spacing).x;

        if (c == '\n' || lineWidth + charWidth >= wrapWidth) {
            wrappedLines.push_back(currentLine);
            currentLine.clear();
            lineWidth = 0.0f;
        }

        if (c != '\n') {
            currentLine += c;
            lineWidth += charWidth;
        }
    }

    if (!currentLine.empty()) {
        wrappedLines.push_back(currentLine);
    }

    return wrappedLines;
}

// Raylib's Remap function
float Remap(float value, float inputStart, float inputEnd, float outputStart, float outputEnd) {
    return outputStart + (value - inputStart) * (outputEnd - outputStart) / (inputEnd - inputStart);
}

int main(int argc, char *argv[]) {
    // --- Initialization ---
    int FONT_SIZE = 50;
    const float FONT_SPACING = 0.5f;
    const int BUTTON_PADDING = 20;
    const int INCREASED_TRANSPARENCY_ALPHA = 50; // More transparent
    const Color BUTTON_COLOR = { 64, 64, 64, (unsigned char)INCREASED_TRANSPARENCY_ALPHA };
    const Color TEXT_GRAY_COLOR = { 150, 150, 150, 255 };
    std::vector<std::string> errorLines;

    // Handle optional file path argument
    const char* filePath = (argc > 1) ? argv[1] : nullptr;

    initApp("TSK Extractor", 30);

    // Load font with initial size for Exit button calculation
    Font initialFont = LoadFontEx("/data/openpilot/selfdrive/assets/fonts/Inter-Regular.ttf", FONT_SIZE * 2, 0, 0);

    if (!initialFont.baseSize) {
      errorLines.push_back("Failed to load font");
      // Continue execution to display the error message
    }

    Font regularFont = initialFont;
    SetTextureFilter(regularFont.texture, TEXTURE_FILTER_ANISOTROPIC_4X);


    SetTargetFPS(30);

    // --- Positioning Variables ---
    const int SCROLLBAR_WIDTH = 15 * 3; // Tripled scrollbar width
    const int RIGHT_SIDE_MARGIN = 20;
    // Removed LEFT_MARGIN

    // --- Exit Button ---
    const std::string exitText = "Exit";
    // Calculate exit button size based on initial font size
    Vector2 exitTextSize = MeasureTextEx(initialFont, exitText.c_str(), FONT_SIZE, FONT_SPACING);
    float exitButtonWidth = exitTextSize.x + 2 * BUTTON_PADDING;
    float exitButtonHeight = exitTextSize.y + BUTTON_PADDING;
    Rectangle exitButtonRect = {
        (float)GetScreenWidth() - exitButtonWidth - RIGHT_SIDE_MARGIN, BUTTON_PADDING / 2.0f,
        exitButtonWidth, exitButtonHeight
    };

    // --- Text Content ---
    std::vector<std::string> constitutionLines = LoadTextFromFile(filePath);
    std::string constitutionText = "";
    for (const std::string& line : constitutionLines) {
        constitutionText += line + "\n";
    }

    // --- Text Box ---
    float textY = exitButtonRect.y + exitButtonRect.height; // Start text immediately below Exit button
    float lineSpacing = FONT_SIZE + FONT_SPACING;
    float touchStartY = 0.0f;
    float textYStart = 0.0f;
    bool isDragging = false;

    // --- Scrollbar ---
    Color scrollbarTrackColor = { 100, 100, 100, (unsigned char)INCREASED_TRANSPARENCY_ALPHA };
    Color scrollbarThumbColor = { 200, 200, 200, (unsigned char)INCREASED_TRANSPARENCY_ALPHA };

    // --- Font Size Buttons ---
    const std::string plusText = "+";
    const std::string minusText = "-";

    // Keep a fixed button size based on initial calculation of the exit button
    float buttonWidth = exitButtonWidth;
    float buttonFontSize = buttonWidth * 0.6f;
    Vector2 plusTextSize = MeasureTextEx(regularFont, plusText.c_str(), buttonFontSize, FONT_SPACING);
    Vector2 minusTextSize = MeasureTextEx(regularFont, minusText.c_str(), buttonFontSize, FONT_SPACING);
    float buttonHeight = 3 * exitButtonRect.height;

    Rectangle plusButtonRect = {
        (float)GetScreenWidth() - buttonWidth - RIGHT_SIDE_MARGIN, GetScreenHeight() - 2 * buttonHeight - 2 * BUTTON_PADDING,
        buttonWidth, buttonHeight
    };
    Rectangle minusButtonRect = {
        (float)GetScreenWidth() - buttonWidth - RIGHT_SIDE_MARGIN, GetScreenHeight() - buttonHeight - BUTTON_PADDING,
        buttonWidth, buttonHeight
    };

    // --- Main Game Loop ---
    while (!WindowShouldClose()) {
        // --- Update ---

        // Calculate wrap width
        float wrapWidth = GetScreenWidth() - RIGHT_SIDE_MARGIN - SCROLLBAR_WIDTH; // Wrap before UI elements, no left margin

        std::vector<std::string> wrappedLines = WrapText(regularFont, constitutionText, FONT_SIZE, FONT_SPACING, wrapWidth);
        int firstVisibleLineIndex = 0;
        if (textY < 0) {
            firstVisibleLineIndex = (int)((-textY) / lineSpacing);
        }

        // Exit Button Logic
        if (CheckCollisionPointRec(GetMousePosition(), exitButtonRect) && IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) {
            break;
        }

        // Font Size Buttons Logic
        if (CheckCollisionPointRec(GetMousePosition(), plusButtonRect) && IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) {
            FONT_SIZE += 10;
            regularFont = LoadFontEx("/data/openpilot/selfdrive/assets/fonts/Inter-Regular.ttf", FONT_SIZE * 2, 0, 0);
            SetTextureFilter(regularFont.texture, TEXTURE_FILTER_ANISOTROPIC_4X);

            lineSpacing = FONT_SIZE + FONT_SPACING;

            // Keep Exit button size, position and text size unchanged

            // Adjust textY to keep the first visible line at the same position
            wrappedLines = WrapText(regularFont, constitutionText, FONT_SIZE, FONT_SPACING, wrapWidth);
            float newTextY = 0;
            for (int i = 0; i < firstVisibleLineIndex; ++i) {
                newTextY -= lineSpacing;
            }
            textY = newTextY;
        }

        if (CheckCollisionPointRec(GetMousePosition(), minusButtonRect) && IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) {
            FONT_SIZE -= 10;
            regularFont = LoadFontEx("/data/openpilot/selfdrive/assets/fonts/Inter-Regular.ttf", FONT_SIZE * 2, 0, 0);
            SetTextureFilter(regularFont.texture, TEXTURE_FILTER_ANISOTROPIC_4X);

            lineSpacing = FONT_SIZE + FONT_SPACING;

            // Keep Exit button size, position and text size unchanged

            // Adjust textY to keep the first visible line at the same position
            wrappedLines = WrapText(regularFont, constitutionText, FONT_SIZE, FONT_SPACING, wrapWidth);
            float newTextY = 0;
            for (int i = 0; i < firstVisibleLineIndex; ++i) {
                newTextY -= lineSpacing;
            }
            textY = newTextY;
        }

        // Touch Dragging Logic
        if (IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) {
            touchStartY = GetMouseY();
            textYStart = textY;
            isDragging = true;
        }
        if (IsMouseButtonDown(MOUSE_BUTTON_LEFT) && isDragging) {
            float deltaY = GetMouseY() - touchStartY;
            textY = textYStart + deltaY;
        } else {
            isDragging = false;
        }

        // Limit scrolling
        float textHeight = (errorLines.empty() ? wrappedLines.size() : errorLines.size()) * lineSpacing;

        if (textY < GetScreenHeight() - textHeight - plusButtonRect.height - BUTTON_PADDING) {
            textY = GetScreenHeight() - textHeight - plusButtonRect.height - BUTTON_PADDING;
        }

        // Allow text to go up to the Exit button without padding
        if (textY > exitButtonRect.y + exitButtonRect.height) {
            textY = exitButtonRect.y + exitButtonRect.height;
        }

        // --- Draw ---
        BeginDrawing();

        ClearBackground(RAYLIB_BLACK);

        // Draw Text Content or Error Messages
        float textDrawingX = 0; // Start at the very left edge
        float textDrawingY = textY;

        if (!errorLines.empty()) {
            float currentY = textDrawingY;
            for (const std::string& line : errorLines) {
                std::vector<std::string> wrappedErrorLines = WrapText(regularFont, line, FONT_SIZE, FONT_SPACING, wrapWidth);
                for (const std::string& wrappedLine : wrappedErrorLines) {
                    DrawTextEx(regularFont, wrappedLine.c_str(), {textDrawingX, currentY}, FONT_SIZE, FONT_SPACING, RAYLIB_RED);
                    currentY += lineSpacing;
                }
            }
        } else {
            // Draw text starting from the first visible line
            float currentY = textDrawingY;
            for (size_t i = firstVisibleLineIndex; i < wrappedLines.size(); ++i) {
                DrawTextEx(regularFont, wrappedLines[i].c_str(), {textDrawingX, currentY}, FONT_SIZE, FONT_SPACING, RAYLIB_RAYWHITE);
                currentY += lineSpacing;
            }
        }

        // --- Scrollbar ---
        float scrollbarX = GetScreenWidth() - SCROLLBAR_WIDTH - RIGHT_SIDE_MARGIN; // Against the right edge
        if (textHeight > GetScreenHeight() - exitButtonRect.height - plusButtonRect.height - 2*BUTTON_PADDING) {
            float scrollbarTrackY = exitButtonRect.y + exitButtonRect.height;
            float scrollbarTrackHeight = plusButtonRect.y - scrollbarTrackY - BUTTON_PADDING;

            // Calculate thumb height and position
            float scrollbarThumbHeight = scrollbarTrackHeight * ((GetScreenHeight() - exitButtonRect.height - plusButtonRect.height - 2*BUTTON_PADDING) / textHeight);
            float scrollbarThumbY = scrollbarTrackY + Remap(textY, exitButtonRect.y + exitButtonRect.height, GetScreenHeight() - textHeight - plusButtonRect.height- BUTTON_PADDING, 0, scrollbarTrackHeight - scrollbarThumbHeight);


            // Ensure minimum thumb height
            scrollbarThumbHeight = std::max(scrollbarThumbHeight, 20.0f);

            // Draw scrollbar track (semi-transparent)
            DrawRectangle((int)scrollbarX, (int)scrollbarTrackY, SCROLLBAR_WIDTH, (int)scrollbarTrackHeight, scrollbarTrackColor);

            // Draw scrollbar thumb (semi-transparent)
            DrawRectangle((int)scrollbarX, (int)scrollbarThumbY, SCROLLBAR_WIDTH, (int)scrollbarThumbHeight, scrollbarThumbColor);
        }

        // Draw Exit Button
        DrawRectangleRec(exitButtonRect, BUTTON_COLOR);
        // Use initialFont for drawing Exit text to keep its size constant
        DrawTextEx(initialFont, exitText.c_str(),
                   {exitButtonRect.x + BUTTON_PADDING, exitButtonRect.y + BUTTON_PADDING / 2.0f},
                   FONT_SIZE, FONT_SPACING, TEXT_GRAY_COLOR);

        // Draw Font Size Buttons (positions are fixed)
        DrawRectangleRec(plusButtonRect, BUTTON_COLOR);
        DrawTextEx(regularFont, plusText.c_str(),
                   {plusButtonRect.x + plusButtonRect.width / 2 - plusTextSize.x / 2, plusButtonRect.y + plusButtonRect.height / 2 - plusTextSize.y / 2},
                   buttonFontSize, FONT_SPACING, TEXT_GRAY_COLOR);

        DrawRectangleRec(minusButtonRect, BUTTON_COLOR);
        DrawTextEx(regularFont, minusText.c_str(),
                   {minusButtonRect.x + minusButtonRect.width / 2 - minusTextSize.x / 2, minusButtonRect.y + minusButtonRect.height / 2 - minusTextSize.y / 2},
                   buttonFontSize, FONT_SPACING, TEXT_GRAY_COLOR);

        EndDrawing();
    }

    // --- De-Initialization ---
    UnloadFont(regularFont);
    UnloadFont(initialFont);
    CloseWindow();

    return 0;
}
