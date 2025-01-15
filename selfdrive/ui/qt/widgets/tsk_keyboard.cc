#include "selfdrive/ui/qt/widgets/tsk_keyboard.h"

#include "common/params.h"
#include "selfdrive/ui/qt/api.h"
#include "selfdrive/ui/qt/widgets/input.h"

TSKKeyboard::TSKKeyboard() :
  ButtonControl("TSK Keyboard (tap to see installed)", "INSTALL", "") {

  QObject::connect(this, &ButtonControl::clicked, [=]() {
    setEnabled(false);

    QString installed = QString::fromStdString(params.get("SecOCKey"));
    QString archived = getArchive();

    QString defaultText = "";
    if (installed.length()) {
      // Currently installed is the preferred default text
      defaultText = installed;
    } else if (archived.length()) {
      // Else, use the archived key if exists
      defaultText = archived;
    }

    // Show the archived key as a hint
    QString subtitle = "";
    if (archived.length()) {
      subtitle = QString("Archived key: ") +  archived;
    }

    QString key = InputDialog::getText("Enter your Toyota Security Key", this, subtitle, false, 32, defaultText);
    if (key.length() != 0) {
      if (isValid(key)) {
        params.put("SecOCKey", key.toStdString());
      } else {
        ConfirmationDialog::alert(tr("Invalid key: %1").arg(key), this);
      }
    }

    refresh(); // Live update
  });

  refresh(); // Initial draw
}

void TSKKeyboard::refresh() {
  QString key = QString::fromStdString(params.get("SecOCKey"));
  if (!key.length()) {
    key = "Not Installed";
  }
  setDescription(key);
  setEnabled(true);
}

QString TSKKeyboard::getArchive() {
  QFile archiveFile("/persist/tsk/key");

  // Archived key file doesn't exist
  if (!archiveFile.open(QIODevice::ReadOnly | QIODevice::Text)) {
    return "";
  }

  QTextStream in(&archiveFile);
  QString key = in.readAll();
  archiveFile.close();

  // Archived key file can't be read
  if (in.status() != QTextStream::Ok) {
    return "";
  }

  // Archived key is not a valid key
  if (!isValid(key)) {
    return "";
  }

  // Return the key
  return key;
}

// Check if the key is a 32 characters long hexadecimal string
bool TSKKeyboard::isValid(QString key) {
  if (key.length() != 32) {
    return false;
  }

  // Check if each character is a valid hexadecimal digit (0-9, a-f)
  for (QChar c : key) {
    if (!c.isDigit() && !(c.isLower() && c >= 'a' && c <= 'f')) {
      return false;
    }
  }

  return true;
}
