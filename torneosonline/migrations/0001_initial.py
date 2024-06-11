# Generated by Django 4.2.11 on 2024-05-23 19:00

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import torneosonline.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(max_length=100, unique=True, verbose_name='Nombre de Usuario')),
                ('email', models.EmailField(max_length=250, unique=True, verbose_name='Correo Electrónico')),
                ('nombre', models.CharField(blank=True, max_length=200, null=True, verbose_name='Nombre')),
                ('apellidos', models.CharField(blank=True, max_length=50, null=True, verbose_name='Apellidos')),
                ('imagen', models.ImageField(default='perfiles/default_img_profile.jpg', upload_to=torneosonline.models.Usuario.directorioImgPerfiles, verbose_name='Imagen de Perfil')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name_plural': 'Usuarios',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Videojuego',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre')),
                ('imagen', models.ImageField(upload_to=torneosonline.models.Videojuego.directorioImgVideojuegos, verbose_name='Imagen del Videojuego')),
            ],
            options={
                'verbose_name_plural': 'Videojuegos',
            },
        ),
        migrations.CreateModel(
            name='Torneo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre')),
                ('fecha', models.DateTimeField(null=True, verbose_name='Fecha')),
                ('numerojugadores', models.IntegerField(verbose_name='Número de Jugadores')),
                ('usuarios', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
                ('videojuego', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='torneosonline.videojuego')),
            ],
            options={
                'verbose_name_plural': 'Torneos',
            },
        ),
        migrations.CreateModel(
            name='Partida',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(null=True, verbose_name='Fecha')),
                ('resultado', models.CharField(max_length=50)),
                ('torneo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='torneosonline.torneo')),
            ],
            options={
                'verbose_name_plural': 'Partidas',
            },
        ),
        migrations.CreateModel(
            name='Logro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre')),
                ('imagen', models.ImageField(upload_to='logros/', verbose_name='Imagen del logro')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Logros',
            },
        ),
        migrations.CreateModel(
            name='Historial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('torneos', models.ManyToManyField(blank=True, to='torneosonline.torneo')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Historiales',
            },
        ),
        migrations.CreateModel(
            name='Amonestacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.TextField()),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Amonestaciones',
            },
        ),
    ]
