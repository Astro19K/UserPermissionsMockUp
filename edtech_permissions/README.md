# EdTech Permissions Synchronization Engine

This is a standalone Django plugin for Open edX that acts as a custom Role-Based Access Control (RBAC) overlay. It provides a "Matrix" interface in the Django Admin where administrators can define custom roles (e.g. "Course Creator", "Global Staff", "Instructor") and assign them specific permissions. 

Crucially, this plugin features a **Synchronization Engine** built with Django Signals. When a custom role is assigned to a native Open edX user, the engine automatically translates those permissions into native Open edX grants (like `auth.Group` memberships, `CourseAccessRole` records, and `is_staff` flags) without requiring modifications to the core `edx-platform` codebase.

## 🚀 Installation & Setup for Teammates

If you are cloning this repository to a fresh Tutor development environment, follow these steps to install the plugin and test the engine.

### 1. Initialize the Environment
If this is your first time running the project, you must initialize the databases and run core migrations before installing plugins:
```bash
tutor dev launch
# If you encounter database connection errors in LMS after launch, restart the services:
tutor dev restart lms cms
```

### 2. Install the Plugin in the Container
Run the following commands to install the plugin into your LMS container and run the necessary database migrations:

```bash
# Copy the plugin into the LMS container
docker cp edtech_permissions tutor_dev-lms-1:/openedx/edtech_permissions
docker exec -t -u root tutor_dev-lms-1 chown -R 1000:1000 /openedx/edtech_permissions

# Install the plugin and run migrations
docker exec -it tutor_dev-lms-1 bash -c "source /openedx/venv/bin/activate && pip install -e /openedx/edtech_permissions && ./manage.py lms makemigrations edtech_permissions && ./manage.py lms migrate edtech_permissions"

# Restart the LMS so it detects the newly installed plugin
tutor dev restart lms
```

### 3. Populate the Database (17 Permissions Matrix)
We have included an automated script that fully populates the Django database to match the 17-column custom Permissions Matrix.

```bash
# Generate 17 Permissions, 12 Roles, and 12 Fake Test Accounts instantly!
docker exec -it tutor_dev-lms-1 bash -c "source /openedx/venv/bin/activate && python /openedx/edtech_permissions/setup_test_users.py"
```

### 4. Install and Start the Course Authoring MFE
Modern versions of Open edX require the Course Authoring Micro-Frontend (MFE) to use the Studio dashboard. Without this, Studio will redirect you to a broken `localhost:2001` link.
```bash
# Install the MFE plugin
pip install tutor-mfe

# Enable the plugin and save config
tutor plugins enable mfe
tutor config save

# Start the LMS, CMS, and MFE (this may take a few minutes to download the first time)
tutor dev start lms cms mfe -d
```

### 5. Import the Official Demonstration Course
Instead of building a course from scratch to test your permissions on, you can import the official Open edX Demonstration course directly into the database.
```bash
tutor dev do importdemocourse
```
*Note: Because you ran the `setup_test_users.py` script earlier, your test users are automatically enrolled in this specific course on the **Verified** track (which is strictly required by Open edX to test Timed and Proctored exams).*

### 6. Enable "Timed Exams" for the Platform
By default, Tutor disables Timed and Proctored exams to save server memory. To test Instructor-level overrides and Timed Exams, you must enable the feature flag by creating a quick local plugin:

1. Find your Tutor plugins directory by running `tutor plugins printroot` in your terminal.
2. Inside that directory, create a new file called `timed_exams.yml` and paste this exact text into it:
```yaml
name: timed_exams
version: 0.1.0
patches:
  common-env-features: |
    "ENABLE_SPECIAL_EXAMS": true
```
3. Run these commands to turn the plugin on and restart the server:
```bash
tutor plugins enable timed_exams
tutor config save
tutor dev restart cms lms
```

### 7. Content Protection (Anti-Copying in the MFE)
Because the modern Learner Portal uses a React Micro-Frontend (MFE), we cannot easily inject global scripts without rebuilding the entire React image. However, instructors can easily protect specific pages directly in Studio!

1. Log into Studio (`http://studio.local.openedx.io:8001`) and open your course.
2. Go to the Unit you want to protect.
3. Under "Add New Component", click **HTML**, and then **Raw HTML**.
4. Click Edit on the new block, delete the template text, and paste this exact code to disable text highlighting:
```html
<style>
  * {
    -webkit-user-select: none !important;
    -ms-user-select: none !important;
    user-select: none !important;
  }
  img {
    pointer-events: none !important;
  }
</style>
```
5. Click **Save** and **Publish**. When a learner views this page in the MFE, they will be completely blocked from copy-pasting the text!

## 🌍 The Important Guide Links

> [!NOTE]
> **Host Mapping:** By default, Tutor uses `local.openedx.io` which automatically resolves to `127.0.0.1`. You do not need to edit your Windows hosts file.

1. **The Admin Site (Django Admin):** `http://local.openedx.io:8000/admin`
   * **Role Definitions (The Matrix):** `http://local.openedx.io:8000/admin/edtech_permissions/mockrole/` (Use this to create or edit roles like "Instructor" or "Course Creator")
   * **User Assignments:** `http://local.openedx.io:8000/admin/edtech_permissions/userroleassignment/` (Use this to assign the roles to specific users)
2. **The Learner Site (LMS):** `http://local.openedx.io:8000`
   * *Where students go to take courses.*
3. **The Course Creator Site (Studio):** `http://studio.local.openedx.io:8001`
   * *Where instructors and creators go to build courses.*
4. **Learner Account (MFE):** `http://apps.local.openedx.io:1997/account`
   * *The modern Micro-Frontend account settings page.*
5. **Learner Profile (MFE):** `http://apps.local.openedx.io:1995/profile`
   * *The modern Micro-Frontend public profile page.*

## 🔑 Test Credentials
All fake accounts use the standard password: `edx`

* **Admin Account:** `admin@example.com` | Password: `admin`
* **Learner:** `fake_learner@example.com` 
* **Course Creator:** `fake_course_creator@example.com`
* **Global Staff:** `fake_global_staff@example.com`
* **Superuser:** `fake_superuser@example.com`
* **Report Manager:** `fake_report_manager@example.com`
* **Beta Tester:** `fake_beta_tester@example.com`
* **Course Staff:** `fake_course_staff@example.com`
* **Instructor:** `fake_instructor@example.com`
* **Discussion Moderator:** `fake_discussion_moderator@example.com`
* **Discussion Admin:** `fake_discussion_admin@example.com`
* **Community TA:** `fake_community_ta@example.com`
* **Group Moderator:** `fake_group_moderator@example.com`

---

## 🧪 How to Test Each Role & Open edX Native Constraints

Open edX natively only supports about 7 distinct course roles. Because your Custom Matrix has **17 highly granular permissions**, our synchronization engine groups some of them together. Here is a breakdown of what you can test for each Fake Account, and the specific Open edX platform constraints you should be aware of.

### 1. The Learner (`fake_learner`)
* **Open edX Native Constraints:** None. This is a standard student.
* **How to Test:** Log into the LMS (`http://local.openedx.io:8000`) and click into the Demo Course. Verify they can watch videos and answer questions, but have no access to Studio or the Instructor Dashboard.

### 2. The Course Creator (`fake_course_creator`)
* **Open edX Native Constraints:** None.
* **How to Test:** Log into Studio (`http://studio.local.openedx.io:8001`). Verify you can see the **"+ New Course"** button on the dashboard to build courses from scratch.

### 3. Global Staff & Superuser (`fake_global_staff`, `fake_superuser`)
* **Open edX Native Constraints:** None. 
* **How to Test:** Go to `http://local.openedx.io:8000/admin`. Verify you can log in and view the backend database tables.

### 4. Course Staff & Instructor (`fake_course_staff`, `fake_instructor`)
* **Open edX Native Constraints:** Open edX treats Staff and Instructors very similarly. Both get full Studio Authoring rights.
* **How to Test:** Log into Studio and open the Demo Course. Verify you can add HTML components, upload videos, and change grading policies. In the LMS, verify you can access the "Instructor Dashboard".

### 5. Beta Tester (`fake_beta_tester`)
* **Open edX Native Constraints:** None.
* **How to Test:** In Studio, set the Start Date of a course to next month. Log into the LMS as the Beta Tester. Verify they bypass the start date lock and can view/test the course early!

### 6. The Forum Team (`fake_discussion_moderator`, `fake_discussion_admin`, `fake_community_ta`)
* **Open edX Native Constraints:** Open edX only has two main forum roles: `forum_admin` and `community_ta`. The granular difference between "Full Forum Admin" and "Moderate Forums" in your spreadsheet is flattened into `forum_admin`.
* **How to Test:** Log into the LMS and go to the **Discussion** tab in the course. Verify these users have special Admin buttons to **Pin, Endorse, or Delete** student posts. 
* **Crucial Security Test:** Try to log into Studio with these accounts. Verify they are **completely blocked** from editing course content (which prevents them from deleting the anti-copying script!).

### 7. Report Manager (`fake_report_manager`)
* **Open edX Native Constraints:** Your spreadsheet separates "Generate Reports", "View Published Reports", and "View Draft Reports". Open edX cannot differentiate these; they are all grouped into the native `data_researcher` role.
* **How to Test:** Log into the LMS and click the **Instructor Dashboard**. Click on the **Data Download** tab. Verify they can download CSV reports of student grades, but verify they are **blocked** from accessing Studio to edit the course.

### 8. Facilities Management
* **Open edX Native Constraints:** Open edX does not have a "Facilities" feature built-in. 
* **How to Test:** The "Can Manage Facilities" checkbox in the Matrix is currently a visual placeholder only. It cannot be tested functionally.

---

### Testing Dynamic Revocation (The "Kill Switch")
1. Log into Django Admin (`http://local.openedx.io:8000/admin`) as `admin`.
2. Go to **Mock roles** and click on **Course Creator**.
3. Uncheck the "Create courses" permission and save.
4. **Verify:** Refresh Studio as `fake_course_creator`. The `+ New Course` button will instantly vanish. The Sync Engine automatically revoked their Open edX privileges because the Matrix definition changed!

---

## 🛠 Troubleshooting Common Errors

### "Mismatching redirect URI" when logging into Studio
If you try to log into Studio and receive an `Error: invalid_request - Mismatching redirect URI` screen, it means the Single Sign-On (SSO) configuration in your local database does not match the URL you are using in your browser.

**How to fix:**
1. Go to your local Django Admin panel (`http://local.openedx.io:8000/admin`).
2. Scroll down to **Django OAuth Toolkit** and click on **Applications**.
3. Click on the application with the Client ID **`cms-sso-dev`**.
4. In the **Redirect uris** text box, add your exact `studio.local.openedx.io` URL on a new line below the existing ones:
   ```text
   http://localhost:8001/complete/edx-oidc/
   http://studio.local.openedx.io:8001/complete/edx-oidc/
   ```
5. Click **Save**. 
6. Go back to Studio (`http://studio.local.openedx.io:8001`) and try logging in again. The SSO will now succeed!

### "localhost refused to connect" or redirect to localhost:2001
If you log into Studio or the LMS and suddenly see an error page saying `localhost refused to connect`, with an address bar showing `localhost:2001` or `localhost:1995`, this is because Open edX relies on Micro-Frontend (MFE) apps for the modern dashboard.
**How to fix:**
You must start the MFE servers! Follow the instructions in **Step 3 of the Installation Guide** to enable the `mfe` plugin and run `tutor dev start mfe -d`.
