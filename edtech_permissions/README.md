# EdTech Permissions Synchronization Engine

This is a standalone Django plugin for Open edX that acts as a custom Role-Based Access Control (RBAC) overlay. It provides a "Matrix" interface in the Django Admin where administrators can define custom roles (e.g. "Course Creator", "Global Staff", "Instructor") and assign them specific permissions. 

Crucially, this plugin features a **Synchronization Engine** built with Django Signals. When a custom role is assigned to a native Open edX user, the engine automatically translates those permissions into native Open edX grants (like `auth.Group` memberships, `CourseAccessRole` records, and `is_staff` flags) without requiring modifications to the core `edx-platform` codebase.

## 🚀 Installation & Setup for Teammates

If you are cloning this repository to a fresh Tutor development environment, follow these steps to install the plugin and test the engine.

### 1. Install the Plugin in the Container
Run the following commands to install the plugin into your LMS container and run the necessary database migrations:

```bash
# Copy the plugin into the LMS container
docker cp edtech_permissions tutor_dev-lms-1:/openedx/edtech_permissions
docker exec -t -u root tutor_dev-lms-1 chown -R 1000:1000 /openedx/edtech_permissions

# Install the plugin and run migrations
docker exec -it tutor_dev-lms-1 bash -c "source /openedx/venv/bin/activate && pip install -e /openedx/edtech_permissions && ./manage.py lms makemigrations edtech_permissions && ./manage.py lms migrate edtech_permissions"
```

### 2. Populate the Database
We have included automated scripts to generate test users and populate the Matrix with default roles and permissions so you don't have to type them all out.

```bash
# 1. Generate the test users (fake_student_1, fake_student_2, fake_instructor)
docker exec -it tutor_dev-lms-1 bash -c "source /openedx/venv/bin/activate && python /openedx/edtech_permissions/setup_test_users.py"

# 2. Populate the Permission Matrix
docker exec -it tutor_dev-lms-1 bash -c "source /openedx/venv/bin/activate && python /openedx/edtech_permissions/update_mock_data.py"
```

### 3. Install and Start the Course Authoring MFE
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

## 🌍 The Important Guide Links

> [!NOTE]
> **Host Mapping Required:** You must map these domains to `127.0.0.1` in your Windows hosts file. To do this automatically, open PowerShell as an **Administrator** and run this single command:
> ```powershell
> Add-Content -Path "C:\Windows\System32\drivers\etc\hosts" -Value "`n127.0.0.1 www.myopenedx.com studio.www.myopenedx.com apps.www.myopenedx.com preview.www.myopenedx.com"
> ```

1. **The Admin Site (Django Admin):** `http://www.myopenedx.com:8000/admin`
   * **Role Definitions (The Matrix):** `http://www.myopenedx.com:8000/admin/edtech_permissions/mockrole/` (Use this to create or edit roles like "Instructor" or "Course Creator")
   * **User Assignments:** `http://www.myopenedx.com:8000/admin/edtech_permissions/userroleassignment/` (Use this to assign the roles to specific users)
2. **The Learner Site (LMS):** `http://www.myopenedx.com:8000`
   * *Where students go to take courses.*
3. **The Course Creator Site (Studio):** `http://studio.www.myopenedx.com:8001`
   * *Where instructors and creators go to build courses.*
4. **Learner Account (MFE):** `http://apps.www.myopenedx.com:1997`
   * *The modern Micro-Frontend account settings page.*
5. **Learner Profile (MFE):** `http://apps.www.myopenedx.com:1995`
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
1. Go to your local Django Admin panel (`http://www.myopenedx.com:8000/admin`).
2. Log in with your admin credentials (e.g., `admin` / `admin`).
3. Scroll to the **EdTech Permissions Mockup** section and click **User role assignments**.
4. Click **Add user role assignment**.
5. Select `fake_student_1`, select the **Course Creator** role, and click **Save**.
6. **Verify:** Go to Open edX Studio (`http://studio.www.myopenedx.com:8001`) and log in as `student1@example.com` (`edx`). You will now see the `+ New Course` button because the Sync Engine automatically added them to the native `course_creator` group.

### Testing a Course Role (e.g., Instructor)
Course roles apply only to a specific course.
1. In Django Admin, go to **User role assignments** -> **Add**.
2. Select `fake_instructor`, select the **Instructor** role.
3. In the **Course ID** field, paste a valid course ID (e.g., `course-v1:edX+DemoX+Demo_Course`). Click **Save**.
4. **Verify:** Log into Studio as `instructor@example.com` (`edx`). You will instantly have access to edit that specific course.

### Testing Dynamic Revocation
1. Log into Django Admin and go to **Mock roles**.
2. Click on **Course Creator**.
3. Uncheck the "Create courses" permission and save.
4. **Verify:** If you refresh Studio as `student1`, the `+ New Course` button will be gone. The Sync Engine automatically revoked their Open edX privileges because the Matrix definition changed.

---

## 🛠 Troubleshooting Common Errors

### "Mismatching redirect URI" when logging into Studio
If you try to log into Studio and receive an `Error: invalid_request - Mismatching redirect URI` screen, it means the Single Sign-On (SSO) configuration in your local database does not match the URL you are using in your browser.

**How to fix:**
1. Go to your local Django Admin panel (`http://www.myopenedx.com:8000/admin`).
2. Scroll down to **Django OAuth Toolkit** and click on **Applications**.
3. Click on the application with the Client ID **`cms-sso-dev`**.
4. In the **Redirect uris** text box, add your exact `studio.www.myopenedx.com` URL on a new line below the existing ones:
   ```text
   http://localhost:8001/complete/edx-oidc/
   http://studio.www.myopenedx.com:8001/complete/edx-oidc/
   ```
5. Click **Save**. 
6. Go back to Studio (`http://studio.www.myopenedx.com:8001`) and try logging in again. The SSO will now succeed!

### "localhost refused to connect" or redirect to localhost:2001
If you log into Studio or the LMS and suddenly see an error page saying `localhost refused to connect`, with an address bar showing `localhost:2001` or `localhost:1995`, this is because Open edX relies on Micro-Frontend (MFE) apps for the modern dashboard.
**How to fix:**
You must start the MFE servers! Follow the instructions in **Step 3 of the Installation Guide** to enable the `mfe` plugin and run `tutor dev start mfe -d`.
