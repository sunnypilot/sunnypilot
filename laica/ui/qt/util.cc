/**
 * Laica-specific UI utility overrides
 */

#include "selfdrive/ui/qt/util.h"

// Override getBrand to return "laica"
QString getBrand() {
  return QObject::tr("LAICa");
}

