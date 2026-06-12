from django.db import migrations, models
import random


def assign_login_ids(apps, schema_editor):
    User = apps.get_model("users", "User")
    rng = random.SystemRandom()
    used = set(
        User.objects.exclude(login_id__isnull=True)
        .exclude(login_id="")
        .values_list("login_id", flat=True)
    )

    for user in User.objects.filter(models.Q(login_id__isnull=True) | models.Q(login_id="")):
        while True:
            login_id = str(rng.randrange(10_000_000, 100_000_000))
            if login_id not in used:
                used.add(login_id)
                user.login_id = login_id
                user.save(update_fields=["login_id"])
                break


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_user_country_user_email_verified_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="login_id",
            field=models.CharField(blank=True, editable=False, max_length=8, null=True, unique=True),
        ),
        migrations.RunPython(assign_login_ids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="login_id",
            field=models.CharField(blank=True, editable=False, max_length=8, unique=True),
        ),
    ]
