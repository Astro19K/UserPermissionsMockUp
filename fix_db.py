from django.db import connection
from edtech_permissions.models import Facility, UserFacilityMapping, AssessmentReport

with connection.schema_editor() as schema_editor:
    try:
        schema_editor.create_model(Facility)
        print("Facility table created.")
    except Exception as e:
        print("Facility error:", e)
        
    try:
        schema_editor.create_model(UserFacilityMapping)
        print("UserFacilityMapping table created.")
    except Exception as e:
        print("UserFacilityMapping error:", e)
        
    try:
        schema_editor.create_model(AssessmentReport)
        print("AssessmentReport table created.")
    except Exception as e:
        print("AssessmentReport error:", e)
