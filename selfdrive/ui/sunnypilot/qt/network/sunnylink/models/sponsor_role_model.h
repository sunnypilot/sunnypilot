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

enum class SponsorTier {
  Free,
  Novice,
  Supporter,
  Contributor,
  Benefactor,
  Guardian,
};

// haha, a role model xD
class SponsorRoleModel final : RoleModel {
public:
  SponsorTier roleTier;

  explicit SponsorRoleModel(const RoleType &roleType, const SponsorTier &roleTier) : RoleModel(roleType), roleTier(roleTier) {}
  explicit SponsorRoleModel(const QJsonObject &json) : RoleModel(json), roleTier(stringToSponsorTier(json["role_tier"].toString())) {}

  [[nodiscard]] QJsonObject toJson() const {
    QJsonObject json = RoleModel::toJson();
    json["role_tier"] = sponsorTierToString(roleTier);
    return json;
  }

  static SponsorTier stringToSponsorTier(const QString &sponsorTierString) {
    const auto sponsorTierStringLower = sponsorTierString.toLower();
    if (sponsorTierStringLower == "guardian")
      return SponsorTier::Guardian;
    if (sponsorTierStringLower == "novice")
      return SponsorTier::Novice;
    if (sponsorTierStringLower == "supporter")
      return SponsorTier::Supporter;
    if (sponsorTierStringLower == "contributor")
      return SponsorTier::Contributor;
    if (sponsorTierStringLower == "benefactor")
      return SponsorTier::Benefactor;

    // Default to Guardian
    return SponsorTier::Free;
  }
  
  static QString sponsorTierToString(const SponsorTier &sponsorTier) {
    switch (sponsorTier) {
      case SponsorTier::Guardian:
        return "Guardian";
      case SponsorTier::Novice:
        return "Novice";
      case SponsorTier::Supporter:
        return "Supporter";
      case SponsorTier::Contributor:
        return "Contributor";
      case SponsorTier::Benefactor:
        return "Benefactor";
      
      default:  // SponsorTier::Free
        return "Free";
    }
  }
  [[nodiscard]] auto getSponsorTierString() const { return sponsorTierToString(roleTier); }

  static QString sponsorTierToColor(const SponsorTier &sponsorTier) {
    switch (sponsorTier) {
      case SponsorTier::Guardian:
        return "gold";
      case SponsorTier::Benefactor:
        return "mediumseagreen";
      case SponsorTier::Contributor:
        return "steelblue";
      case SponsorTier::Supporter:
        return "mediumpurple";
      case SponsorTier::Novice:
        return "white";
      default:  // SponsorTier::Free
        return "silver";
    }
  }
  [[nodiscard]] auto getSponsorTierColor() const { return sponsorTierToColor(roleTier); }
};
