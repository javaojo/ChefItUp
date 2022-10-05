
# Add Google API key to database

# Databases are annoying

from django.db import migrations


# Creates instances of models
def forwards_func(apps, schema_editor):
    print('forwards')
    Sites = apps.get_model("sites", "Site")
    SocialApp = apps.get_model("socialaccount", "SocialApp")

    db_alias = schema_editor.connection.alias

    Sites.objects.using(db_alias).bulk_create([
        Sites(name="localhost", domain="localhost"),
        Sites(name="chefitup", domain="http://chefitup.herokuapp.com/"),
        Sites(name="chefitup", domain="https://chefitup.herokuapp.com/"),
    ])


    social_app_object = SocialApp.objects.create(provider="google", name="GoogleAPI",
                  client_id="701154494060-pvc597bb11gh13tic5oda9cdhedd81n8.apps.googleusercontent.com", key="",
                  secret="VsYL1pzHVhQ5CN1w5CBcxm_Q")

    social_app_object.sites.through.objects.create(socialapp_id=1, site_id= 1)

    social_app_object_2 = SocialApp.objects.create(provider="google", name="GoogleAPI2",
                  client_id="701154494060-pvc597bb11gh13tic5oda9cdhedd81n8.apps.googleusercontent.com", key="",
                  secret="VsYL1pzHVhQ5CN1w5CBcxm_Q")

    social_app_object_2.sites.through.objects.create(socialapp_id=1, site_id=2)


# Deletes instances of models
def reverse_func(apps, schema_editor):
    print('reverse')
    Sites = apps.get_model("sites", "Site")
    SocialApp = apps.get_model("socialaccount", "SocialApp")

    db_alias = schema_editor.connection.alias

    Sites.objects.using(db_alias).filter(name="localhost", domain="localhost").delete()

    Sites.objects.using(db_alias).filter(name="chefitup", domain="http://chefitup.herokuapp.com/").delete()

    SocialApp.objects.using(db_alias).filter(provider="google", name="GoogleAPI",
                                             client_id="701154494060-pvc597bb11gh13tic5oda9cdhedd81n8.apps.googleusercontent.com",
                                             key="", secret="VsYL1pzHVhQ5CN1w5CBcxm_Q").delete()

    SocialApp.objects.using(db_alias).filter(provider="google", name="GoogleAPI2",
                                             client_id="701154494060-pvc597bb11gh13tic5oda9cdhedd81n8.apps.googleusercontent.com",
                                             key="", secret="VsYL1pzHVhQ5CN1w5CBcxm_Q").delete()


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(forwards_func, reverse_func, elidable=False)
    ]
