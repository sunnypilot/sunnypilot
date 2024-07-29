/**
The MIT License

Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Last updated: July 29, 2024
***/

#pragma once

#include <QJsonObject>

enum class RoleType {
  ReadOnly,
  Sponsor,
  Admin
};

// haha, a role model xD
class RoleModel {
protected:
  QJsonObject m_raw_json_object;
  
public:
  RoleType roleType;
  
  explicit RoleModel(const RoleType &roleType) : roleType(roleType) {
    m_raw_json_object = toJson();
  }
  explicit RoleModel(const QJsonObject &json) : RoleModel(stringToRoleType(json["role_type"].toString())) {
    m_raw_json_object = json;
  }

  [[nodiscard]] QJsonObject toJson() const {
    QJsonObject json;
    json["role_type"] = roleTypeToString(roleType);
    return json;
  }

  static RoleType stringToRoleType(const QString &roleTypeString) {
    if (roleTypeString == "ReadOnly") {
      return RoleType::ReadOnly;
    } else if (roleTypeString == "Sponsor") {
      return RoleType::Sponsor;
    } else {  // Default to Admin
      return RoleType::Admin;
    }
  }

  static QString roleTypeToString(const RoleType &roleType) {
    switch (roleType) {
      case RoleType::ReadOnly:
        return "ReadOnly";
      case RoleType::Sponsor:
        return "Sponsor";
      default:  // RoleType::Admin
        return "Admin";
    }
  }
  
  template <typename T, typename = typename std::enable_if<std::is_base_of<RoleModel, T>::value>::type>
  T as() const {
    return T(m_raw_json_object);
  }
};
