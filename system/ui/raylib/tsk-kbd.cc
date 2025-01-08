#include "system/ui/raylib/util.h"
#include <string>
#include <vector>
#include <fstream>
#include <regex>
#include <chrono>
#include <algorithm>
#include <cerrno>
#include <cstring>

// --- Constants ---
const int FONT_SIZE = 100;
const int INSTALLED_LABEL_FONT_SIZE = 80;
const int ERROR_LABEL_FONT_SIZE = 80;
const float FONT_SPACING = 1.0f;
const float INPUT_FONT_SPACING = 3.0f;
const Color GRAY = {96, 96, 96, 255};
const int EXIT_BUTTON_PADDING = 20;
const int INPUT_BOX_PADDING = 20;
const int CHARS_LEFT_LABEL_PADDING = 20;
const int KEY_HEIGHT = 180;
const int KEY_PADDING = 10;
const int NUM_KEYS_FIRST_ROW = 10;
const int NUM_KEYS_SECOND_ROW = 7;
const int INPUT_BOX_CHARS = 32;

// --- Function to convert hex string to Color ---
Color HexToColor(const std::string& hex) {
    if (hex.length() != 7 || hex[0] != '#') {
        return GRAY; // Default to gray if invalid
    }

    unsigned int r, g, b;
    if (sscanf(hex.c_str(), "#%02x%02x%02x", &r, &g, &b) != 3) {
        return GRAY; // Default to gray if invalid
    }

    return {static_cast<unsigned char>(r), static_cast<unsigned char>(g), static_cast<unsigned char>(b), 255};
}


// --- Function to write content to a file and capture error messages ---
std::pair<bool, std::vector<std::string>> writeToFileWithError(const std::string& path, const std::string& content) {
    std::ofstream file(path, std::ios::out | std::ios::trunc);
    std::vector<std::string> errorMessages;
    if (!file.is_open()) {
        errorMessages.push_back("Failed to open file '" + path + "'");
        errorMessages.push_back("Error: " + std::string(strerror(errno)));
        return {false, errorMessages};
    }
    file << content;
    file.close();
    if (!file.good()) {
        errorMessages.push_back("Failed to write to file '" + path + "'");
        errorMessages.push_back("Error: " + std::string(strerror(errno)));
        return {false, errorMessages};
    }
    return {true, {}};
}

// --- Function to read and validate the SecOCKey ---
std::string readSecOCKey() {
    const std::string filePath = "/data/params/d/SecOCKey";
    std::ifstream file(filePath, std::ios::binary | std::ios::ate);

    if (!file.is_open()) {
        return "Installed: None";
    }

    std::streamsize size = file.tellg();
    file.seekg(0, std::ios::beg);
    std::vector<char> buffer(size);
    if (!file.read(buffer.data(), size)) {
        return "Installed: None";
    }

    if (std::any_of(buffer.begin(), buffer.end(), [](char c) { return c < 32 && c != '\n' && c != '\r'; })) {
        return "Installed: Invalid (binary file)";
    }

    std::string content(buffer.begin(), buffer.end());
    content.erase(std::remove(content.begin(), content.end(), '\n'), content.end());

    if (std::regex_match(content, std::regex("^[a-f0-9]{32}$"))) {
        return "Installed: " + content;
    }

    return "Installed: Invalid (" + content + ")";
}

// --- Function to read and validate a 32-character lowercase hexadecimal string from a file ---
std::string readAndValidateKeyFile(const std::string& filePath) {
    std::ifstream file(filePath);
    if (!file.is_open()) {
        return "";
    }

    std::string content;
    file >> content;

    if (std::regex_match(content, std::regex("^[a-f0-9]{32}$"))) {
        return content;
    } else {
        return "";
    }
}

int main(int argc, char* argv[]) {
    const std::string basePath = "/data/openpilot";
    initApp("My Raylib App", 30);

    Font regularFont = LoadFontEx((basePath + "/selfdrive/assets/fonts/Inter-Regular.ttf").c_str(), FONT_SIZE * 2, 0, 0);
    SetTextureFilter(regularFont.texture, TEXTURE_FILTER_ANISOTROPIC_4X);

    if (!regularFont.baseSize) {
        TraceLog(LOG_ERROR, "Failed to load font: %s", (basePath + "/selfdrive/assets/fonts/Inter-Regular.ttf").c_str());
        return 1;
    }

    Font inputFont = LoadFontEx((basePath + "/selfdrive/assets/fonts/Inter-Bold.ttf").c_str(), FONT_SIZE * 2, 0, 0);
    SetTextureFilter(inputFont.texture, TEXTURE_FILTER_ANISOTROPIC_4X);

    if (!inputFont.baseSize) {
        TraceLog(LOG_ERROR, "Failed to load font: %s", (basePath + "/selfdrive/assets/fonts/Inter-SemiBold.ttf").c_str());
        return 1;
    }

    const std::string exitText = "Exit";
    Vector2 exitTextSize = MeasureTextEx(regularFont, exitText.c_str(), FONT_SIZE, FONT_SPACING);
    Rectangle exitButtonRect = {
        GetScreenWidth() - exitTextSize.x - EXIT_BUTTON_PADDING, EXIT_BUTTON_PADDING / 2,
        exitTextSize.x + EXIT_BUTTON_PADDING, exitTextSize.y + EXIT_BUTTON_PADDING
    };

    const int KEYBOARD_Y = GetScreenHeight() - KEY_HEIGHT * 2 - KEY_PADDING * 3;
    const int KEY_WIDTH_FIRST_ROW = (GetScreenWidth() - (NUM_KEYS_FIRST_ROW + 1) * KEY_PADDING) / NUM_KEYS_FIRST_ROW;
    const int KEY_WIDTH_SECOND_ROW = (GetScreenWidth() - (NUM_KEYS_SECOND_ROW + 1) * KEY_PADDING) / NUM_KEYS_SECOND_ROW;

    const int INPUT_BOX_WIDTH = MeasureTextEx(inputFont, "00000000000000000000000000000000", FONT_SIZE, INPUT_FONT_SPACING).x;
    const int INPUT_BOX_HEIGHT = FONT_SIZE + INPUT_BOX_PADDING * 2;
    Rectangle inputBoxRect = {
        (GetScreenWidth() - INPUT_BOX_WIDTH) / 2.0f, (KEYBOARD_Y / 2.0f) - INPUT_BOX_HEIGHT / 2.0f,
        static_cast<float>(INPUT_BOX_WIDTH), static_cast<float>(INPUT_BOX_HEIGHT)
    };

    std::string inputText = readAndValidateKeyFile("/persist/tsk/key");

    std::vector<std::string> keyTexts = {
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
        "a", "b", "c", "d", "e", "f", "<"
    };
    std::vector<Rectangle> keyRects;
    for (size_t i = 0; i < keyTexts.size(); ++i) {
        int row = i < NUM_KEYS_FIRST_ROW ? 0 : 1;
        int col = i < NUM_KEYS_FIRST_ROW ? i % NUM_KEYS_FIRST_ROW : (i - NUM_KEYS_FIRST_ROW) % NUM_KEYS_SECOND_ROW;
        int keyWidth = row == 0 ? KEY_WIDTH_FIRST_ROW : KEY_WIDTH_SECOND_ROW;
        keyRects.push_back({
            static_cast<float>(KEY_PADDING + (keyWidth + KEY_PADDING) * col),
            static_cast<float>(KEYBOARD_Y + (KEY_HEIGHT + KEY_PADDING) * row),
            static_cast<float>(keyWidth),
            static_cast<float>(KEY_HEIGHT)
        });
    }

    bool showCharsLeftLabel = inputText.empty();
    bool showInstallButton = false;
    bool showSuccessLabel = false;
    Rectangle installButtonRect;
    std::string installButtonText = "Install this key";
    std::string successLabelText = "Success!";
    std::vector<std::string> errorLabelLines;
    std::string installedLabel = "Installed: None";

    auto lastUpdateTime = std::chrono::steady_clock::now();
    while (!WindowShouldClose()) {
        auto now = std::chrono::steady_clock::now();
        if (std::chrono::duration_cast<std::chrono::seconds>(now - lastUpdateTime).count() >= 1) {
            installedLabel = readSecOCKey();
            lastUpdateTime = now;
        }

        if (CheckCollisionPointRec(GetMousePosition(), exitButtonRect) && IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) {
            break;
        }

        for (size_t i = 0; i < keyRects.size(); ++i) {
            if (CheckCollisionPointRec(GetMousePosition(), keyRects[i]) && IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) {
                if (keyTexts[i] == "<") {
                    if (!inputText.empty()) {
                        inputText.pop_back();
                        showCharsLeftLabel = inputText.size() < INPUT_BOX_CHARS;
                        showInstallButton = false;
                        showSuccessLabel = false;
                        errorLabelLines.clear();
                    }
                } else if (inputText.size() < INPUT_BOX_CHARS) {
                    inputText += keyTexts[i];
                    showCharsLeftLabel = inputText.size() < INPUT_BOX_CHARS;
                }
            }
        }

        showInstallButton = (inputText.size() == INPUT_BOX_CHARS) && (!showSuccessLabel && errorLabelLines.empty());
        showCharsLeftLabel = inputText.size() < INPUT_BOX_CHARS;

        if (showInstallButton) {
            Vector2 installButtonTextSize = MeasureTextEx(regularFont, installButtonText.c_str(), FONT_SIZE, FONT_SPACING);
            installButtonRect = {
                (GetScreenWidth() - installButtonTextSize.x - 40) / 2.0f, inputBoxRect.y + inputBoxRect.height + CHARS_LEFT_LABEL_PADDING,
                installButtonTextSize.x + 40, installButtonTextSize.y + 20
            };
        }

        if (showInstallButton && CheckCollisionPointRec(GetMousePosition(), installButtonRect) && IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) {
            errorLabelLines.clear();
            auto [successData, errorData] = writeToFileWithError("/data/params/d/SecOCKey", inputText);
            auto [successPersist, errorPersist] = writeToFileWithError("/persist/tsk/key", inputText);

            if (!successData) {
                errorLabelLines.insert(errorLabelLines.end(), errorData.begin(), errorData.end());
            }
            if (!successPersist) {
                errorLabelLines.insert(errorLabelLines.end(), errorPersist.begin(), errorPersist.end());
            }

            if (successData && successPersist) {
                showSuccessLabel = true;
            } else {
                showSuccessLabel = false;
            }

            showInstallButton = false;
        }

        BeginDrawing();
        ClearBackground(RAYLIB_BLACK);

        Vector2 installedLabelSize = MeasureTextEx(regularFont, installedLabel.c_str(), INSTALLED_LABEL_FONT_SIZE, FONT_SPACING);
        DrawTextEx(regularFont, installedLabel.c_str(),
                   {(GetScreenWidth() - installedLabelSize.x) / 2, inputBoxRect.y - installedLabelSize.y - CHARS_LEFT_LABEL_PADDING},
                   INSTALLED_LABEL_FONT_SIZE, FONT_SPACING, RAYLIB_RAYWHITE);

        DrawRectangleRec(exitButtonRect, GRAY);
        DrawTextEx(regularFont, exitText.c_str(),
                   {exitButtonRect.x + EXIT_BUTTON_PADDING / 2, exitButtonRect.y + EXIT_BUTTON_PADDING / 2},
                   FONT_SIZE, FONT_SPACING, RAYLIB_RAYWHITE);

        // Draw the input box with black background and white border
        DrawRectangleRec(inputBoxRect, RAYLIB_BLACK);
        DrawRectangleLinesEx(inputBoxRect, 2, RAYLIB_RAYWHITE); // 2 is the line thickness

        // Calculate the starting position for the text
        float textX = inputBoxRect.x + INPUT_BOX_PADDING;
        float textY = inputBoxRect.y + INPUT_BOX_PADDING;
        float groupSpacing = MeasureTextEx(inputFont, " ", 30, INPUT_FONT_SPACING).x; // Not sure why the spacing is narrower between the groups. Add a little more.

        // Define colors for each group of 4 characters
        std::vector<std::string> DARK_COLORS = {
            "#6A0DAD",
            "#2F4F4F",
            "#556B2F",
            "#8B0000",
            "#1874CD",
            "#006400",
        };

        std::vector<Color> colors;
        for (const std::string& hex : DARK_COLORS) {
            colors.push_back(HexToColor(hex));
        }

        // Draw the input text with colored groups
        for (int i = 0; i < inputText.size(); i += 4) {
            std::string group = inputText.substr(i, 4);
            Color color = colors[(i / 4) % colors.size()];
            DrawTextEx(inputFont, group.c_str(), {textX, textY}, FONT_SIZE, INPUT_FONT_SPACING, color);
            textX += MeasureTextEx(inputFont, group.c_str(), FONT_SIZE, INPUT_FONT_SPACING).x + groupSpacing;
        }

        if (showCharsLeftLabel) {
            int charsLeft = INPUT_BOX_CHARS - inputText.size();
            std::string charsLeftText = std::to_string(charsLeft) + " characters left";
            Vector2 charsLeftTextSize = MeasureTextEx(regularFont, charsLeftText.c_str(), FONT_SIZE, FONT_SPACING);
            DrawTextEx(regularFont, charsLeftText.c_str(),
                       {(GetScreenWidth() - charsLeftTextSize.x) / 2, inputBoxRect.y + inputBoxRect.height + CHARS_LEFT_LABEL_PADDING},
                       FONT_SIZE, FONT_SPACING, RAYLIB_RAYWHITE);
        }

        if (showInstallButton) {
            DrawRectangleRec(installButtonRect, GRAY);
            DrawTextEx(regularFont, installButtonText.c_str(),
                       {installButtonRect.x + 20, installButtonRect.y + 10},
                       FONT_SIZE, FONT_SPACING, RAYLIB_RAYWHITE);
        }

        if (showSuccessLabel) {
            Vector2 successLabelTextSize = MeasureTextEx(regularFont, successLabelText.c_str(), FONT_SIZE, FONT_SPACING);
            DrawTextEx(regularFont, successLabelText.c_str(),
                       {installButtonRect.x + (installButtonRect.width - successLabelTextSize.x) / 2,
                        installButtonRect.y + (installButtonRect.height - successLabelTextSize.y) / 2},
                       FONT_SIZE, FONT_SPACING, RAYLIB_GREEN);
        }

        if (!errorLabelLines.empty()) {
            float errorLabelY = showInstallButton ? installButtonRect.y + installButtonRect.height + CHARS_LEFT_LABEL_PADDING : inputBoxRect.y + inputBoxRect.height + CHARS_LEFT_LABEL_PADDING;
            for (const std::string& line : errorLabelLines) {
                Vector2 errorLabelLineSize = MeasureTextEx(regularFont, line.c_str(), ERROR_LABEL_FONT_SIZE, FONT_SPACING);
                DrawTextEx(regularFont, line.c_str(),
                           {(GetScreenWidth() - errorLabelLineSize.x) / 2, errorLabelY},
                           ERROR_LABEL_FONT_SIZE, FONT_SPACING, RAYLIB_RED);
                errorLabelY += errorLabelLineSize.y;
            }
        }

        for (size_t i = 0; i < keyRects.size(); ++i) {
            DrawRectangleRec(keyRects[i], GRAY);
            Vector2 keyTextSize = MeasureTextEx(regularFont, keyTexts[i].c_str(), FONT_SIZE, FONT_SPACING);
            DrawTextEx(regularFont, keyTexts[i].c_str(),
                       {keyRects[i].x + (keyRects[i].width - keyTextSize.x) / 2, keyRects[i].y + (keyRects[i].height - keyTextSize.y) / 2},
                       FONT_SIZE, FONT_SPACING, RAYLIB_RAYWHITE);
        }

        EndDrawing();
    }

    UnloadFont(regularFont);
    CloseWindow();
    return 0;
}
