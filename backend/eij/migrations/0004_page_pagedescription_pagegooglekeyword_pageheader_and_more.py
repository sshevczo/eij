# Generated by Django 4.2.3 on 2023-12-22 15:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eij', '0003_alter_scenario_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=300)),
                ('title', models.CharField(max_length=300)),
                ('text', models.TextField(blank=True)),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eij.language')),
                ('website', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='eij.website')),
            ],
            options={
                'verbose_name': 'Page',
                'verbose_name_plural': 'Pages',
            },
        ),
        migrations.CreateModel(
            name='PageDescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=90)),
                ('page', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='eij.page')),
            ],
            options={
                'verbose_name': 'Page Description',
                'verbose_name_plural': 'Page Descriptions',
            },
        ),
        migrations.CreateModel(
            name='PageGoogleKeyWord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=70)),
                ('page', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='eij.page')),
            ],
            options={
                'verbose_name': 'Page Google KeyWord',
                'verbose_name_plural': 'Page Google KeyWords',
            },
        ),
        migrations.CreateModel(
            name='PageHeader',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=30)),
                ('page', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='eij.page')),
            ],
            options={
                'verbose_name': 'Page Header',
                'verbose_name_plural': 'Page Headers',
            },
        ),
        migrations.CreateModel(
            name='PageRawKeyWord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=40)),
                ('page', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='eij.page')),
            ],
            options={
                'verbose_name': 'Page Raw KeyWord',
                'verbose_name_plural': 'Page Raw KeyWords',
            },
        ),
        migrations.RemoveField(
            model_name='landing',
            name='language',
        ),
        migrations.RemoveField(
            model_name='landingfeedback',
            name='landing',
        ),
        migrations.RemoveField(
            model_name='landingstep',
            name='landing',
        ),
        migrations.RemoveField(
            model_name='languagemeta',
            name='language',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='language',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='meta',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='taxonomy',
        ),
        migrations.RemoveField(
            model_name='scenariodescription',
            name='scenario',
        ),
        migrations.RemoveField(
            model_name='scenariogooglekeyword',
            name='scenario',
        ),
        migrations.RemoveField(
            model_name='scenarioheader',
            name='scenario',
        ),
        migrations.RemoveField(
            model_name='scenariometatranslated',
            name='language',
        ),
        migrations.RemoveField(
            model_name='scenariorawkeyword',
            name='scenario',
        ),
        migrations.RemoveField(
            model_name='secondleveltaxonomy',
            name='items',
        ),
        migrations.RemoveField(
            model_name='secondleveltaxonomy',
            name='taxonomy',
        ),
        migrations.DeleteModel(
            name='FirstLevelTaxonomy',
        ),
        migrations.DeleteModel(
            name='Landing',
        ),
        migrations.DeleteModel(
            name='LandingFeedback',
        ),
        migrations.DeleteModel(
            name='LandingStep',
        ),
        migrations.DeleteModel(
            name='LanguageMeta',
        ),
        migrations.DeleteModel(
            name='Scenario',
        ),
        migrations.DeleteModel(
            name='ScenarioDescription',
        ),
        migrations.DeleteModel(
            name='ScenarioGoogleKeyWord',
        ),
        migrations.DeleteModel(
            name='ScenarioHeader',
        ),
        migrations.DeleteModel(
            name='ScenarioMetaTranslated',
        ),
        migrations.DeleteModel(
            name='ScenarioRawKeyWord',
        ),
        migrations.DeleteModel(
            name='SecondLevelTaxonomy',
        ),
        migrations.DeleteModel(
            name='TechnologyItem',
        ),
    ]
