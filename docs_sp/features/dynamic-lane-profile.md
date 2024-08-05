# **Dynamic Lane Profile (DLP)**

Dynamic Lane Profile (DLP) aims to provide the best driving experience by confidently keeping the vehicle within a lane. It allows sunnypilot to dynamically switch between lane profiles based on the lane recognition confidence level on the road.

!!! note
    Due to the removal of lateral planner in newer Driving Models, Dynamic Lane Profile is only available with the following selected Driving Models.

    - New Delhi (December 21, 2023) - ND
    - Blue Diamond v2 (December 11, 2023) - BDv2
    - Blue Diamond (November 18, 2023) - BDv1
    - Farmville (November 7, 2023) - FV
    - Night Strike (October 3, 2023) - NS

## **Available Modes**

- **Auto Lane**: sunnypilot dynamically selects between `Laneline` or `Laneless` model.
- **Laneline**: uses the Laneline model only.
- **Laneless**: uses the Laneless model only.

### **Feature Location**

**1. Settings**
![Settings](../assets/features/dlp-1.png)

**2. `sunnypilot` Panel**
![sunnypilot Panel](../assets/features/dlp-2.png)

**3. Select the desired mode**
![DLP Select](../assets/features/dlp-3.png)
