import apps.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("publications", "0002_publication_images"),
    ]

    operations = [
        migrations.AddField(
            model_name="publicationcategory",
            name="image",
            field=models.ImageField(blank=True, help_text="Affichée dans la barre des catégories. Sans photo, l'image de la dernière actualité de la catégorie est utilisée.", upload_to="categories/", validators=[apps.core.validators.validate_image], verbose_name="photo de la catégorie"),
        ),
    ]
