#include "system/ui/raylib/util.h"
#include <cstdlib>
#include <string>

// --- Constants ---
namespace {
  const int kFontSize = 100;
  const float kFontSpacing = 1.0f;
  const Color kGray = RAYLIB_GRAY;
  const Color kWhite = RAYLIB_RAYWHITE;
  const Color kBlack = RAYLIB_BLACK;
  const int kButtonHeight = 300;
  const int kButtonWidth = 600;
  const int kButtonPadding = 40;
  const int kExitButtonPadding = 20;
  const int kExitButtonWidth = 180;
  const int kExitButtonHeight = 80;
  const std::string kBasePath = "/data/openpilot";
  const std::string kFontPath = kBasePath + "/selfdrive/assets/fonts/Inter-Regular.ttf";
  const std::string kExtractButtonText = "Extract key\nfrom the car";
  const std::string kKeyboardButtonText = "Manual Install";
  const std::string kExitText = "Exit";
  const std::string kExtractScriptPath = kBasePath + "/tsk/extract.sh";
  const std::string kKeyboardScriptPath = kBasePath + "/system/ui/tsk-kbd";
}

// Function to draw a button with text
void DrawButton(const Rectangle& rect, const std::string& text, const Font& font, const Color& color) {
  DrawRectangleRec(rect, color);
  Vector2 textSize = MeasureTextEx(font, text.c_str(), kFontSize, kFontSpacing);
  Vector2 textPos = {
      rect.x + (rect.width - textSize.x) / 2,
      rect.y + (rect.height - textSize.y) / 2 // Center text vertically based on actual height
  };
  DrawTextEx(font, text.c_str(), textPos, kFontSize, kFontSpacing, kWhite);
}

int main(int argc, char* argv[]) {
  initApp("TSK Manager", 30);

  // Load font
  Font regularFont = LoadFontEx(kFontPath.c_str(), kFontSize * 2, 0, 0);
  SetTextureFilter(regularFont.texture, TEXTURE_FILTER_ANISOTROPIC_4X);
  if (!regularFont.baseSize) {
    TraceLog(LOG_ERROR, "Failed to load font");
    return 1;
  }

  // Button Rectangles
  Rectangle extractButtonRect = {
      static_cast<float>(GetScreenWidth() / 2 - kButtonWidth - kButtonPadding / 2),
      static_cast<float>(GetScreenHeight() / 2 - kButtonHeight / 2),
      static_cast<float>(kButtonWidth),
      static_cast<float>(kButtonHeight)
  };

  Rectangle keyboardButtonRect = {
      static_cast<float>(GetScreenWidth() / 2 + kButtonPadding / 2),
      static_cast<float>(GetScreenHeight() / 2 - kButtonHeight / 2),
      static_cast<float>(kButtonWidth),
      static_cast<float>(kButtonHeight)
  };

  Rectangle exitButtonRect = {
      static_cast<float>(GetScreenWidth() - kExitButtonWidth - kExitButtonPadding),
      static_cast<float>(kExitButtonPadding),
      static_cast<float>(kExitButtonWidth),
      static_cast<float>(kExitButtonHeight)
  };

  while (!WindowShouldClose()) {
    BeginDrawing();
    ClearBackground(kBlack);

    // Exit Button
    DrawButton(exitButtonRect, kExitText, regularFont, kGray);
    if (CheckCollisionPointRec(GetMousePosition(), exitButtonRect) && IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) {
      break;
    }

    // Extract Button
    DrawButton(extractButtonRect, kExtractButtonText, regularFont, kGray);
    if (CheckCollisionPointRec(GetMousePosition(), extractButtonRect) && IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) {
      system(kExtractScriptPath.c_str());
    }

    // Keyboard Button
    DrawButton(keyboardButtonRect, kKeyboardButtonText, regularFont, kGray);
    if (CheckCollisionPointRec(GetMousePosition(), keyboardButtonRect) && IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) {
      system(kKeyboardScriptPath.c_str());
    }

    EndDrawing();
  }

  UnloadFont(regularFont);
  CloseWindow();
  return 0;
}
