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

### 3. Populate the Database
We have included automated scripts to generate test users and populate the Matrix with default roles and permissions so you don't have to type them all out.

```bash
# 1. Generate the test users (fake_student_1, fake_student_2, fake_instructor)
docker exec -it tutor_dev-lms-1 bash -c "source /openedx/venv/bin/activate && python /openedx/edtech_permissions/setup_test_users.py"

# 2. Populate the Permission Matrix
docker exec -it tutor_dev-lms-1 bash -c "source /openedx/venv/bin/activate && python /openedx/edtech_permissions/update_mock_data.py"
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
* **Admin Account:** `admin@example.com` | Password: `admin`
* **Student 1:** `student1@example.com` | Password: `edx`
* **Student 2:** `student2@example.com` | Password: `edx`
* **Instructor:** `instructor@example.com` | Password: `edx`

---

## 🧪 How to Test Each Role (Step-by-Step)

The synchronization engine automatically applies native Open edX permissions when you assign a role to a user.

### Testing a Platform Role (e.g., Course Creator)
1. Go to your local Django Admin panel (`http://local.openedx.io:8000/admin`).
2. Log in with your admin credentials (e.g., `admin` / `admin`).
3. Scroll to the **EdTech Permissions Mockup** section and click **User role assignments**.
4. Click **Add user role assignment**.
5. Select `fake_student_1`, select the **Course Creator** role, and click **Save**.
6. **Verify:** Go to Open edX Studio (`http://studio.local.openedx.io:8001`) and log in as `student1@example.com` (`edx`). You will now see the `+ New Course` button because the Sync Engine automatically added them to the native `course_creator` group.

### Testing a Course Role (e.g., Instructor)
Course roles apply only to a specific course.
1. In Django Admin, go to **User role assignments** -> **Add**.
2. Select `fake_instructor`, select the **Instructor** role.
3. In the **Course ID** field, paste a valid course ID (e.g., `course-v1:OpenedX+DemoX+DemoCourse`). Click **Save**.
4. **Verify:** Log into Studio as `instructor@example.com` (`edx`). You will instantly have access to edit that specific course.

### Testing Dynamic Revocation
1. Log into Django Admin and go to **Mock roles**.
2. Click on **Course Creator**.
3. Uncheck the "Create courses" permission and save.
4. **Verify:** If you refresh Studio as `student1`, the `+ New Course` button will be gone. The Sync Engine automatically revoked their Open edX privileges because the Matrix definition changed.

### Testing Premium Features (Timed Exams)
Because your test users were automatically enrolled in the **Verified** track (in Step 5), they are eligible for premium exams!
1. Log into Studio (`http://studio.local.openedx.io:8001`) as `instructor@example.com`.
2. Go to **Content -> Outline** and click the Configure (gear) icon on any Subsection.
3. Go to the **Advanced** tab, set it to **Timed**, type `00:05`, and click Save.
4. **Publish** the subsection (click the cloud icon).
5. Log into the LMS (`http://local.openedx.io:8000`) as `student1@example.com` and navigate to that section. You will be hit by a giant Timed Exam blocking screen!
6. **Verify Audit Bypassing:** To prove that free students don't get exams, go to your Django Admin (`http://local.openedx.io:8000/admin`), scroll to **EDTECH PERMISSIONS MOCKUP -> Course enrollments**. Click on `student1`'s record, change their **Mode** from `verified` to `audit`, and click Save. If you refresh the LMS, the timer is magically gone!

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
