from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from ocsa_legacy.models import RegistroNotas
from profile_auth.models import User
from source.models import Note


class Command(BaseCommand):
    help = "Migrate legacy users on RegistroNotas to new User model"

    def handle(self, *args, **kwargs):
        total = RegistroNotas.objects.count()
        not_found = 0
        for registro in RegistroNotas.objects.all():
            owner = registro.owner
            if not owner:
                continue
            user = self.create_user(owner)

            datum = registro.datum
            if not datum:
                continue

            title = datum.get("nota", {}).get("titulo")
            if not title:
                continue
            notes_query = Note.objects.filter(title=title)
            notes_count = notes_query.count()
            if notes_count == 0:
                self.stdout.write(
                    self.style.ERROR(
                        f"Not found: Note with title {title}, owner: {owner}"))

                not_found += 1
                continue
            if notes_count > 1:
                self.stdout.write(
                    self.style.WARNING(
                        f"Multiple notes({notes_count}) with title {title}"))
            Note.objects.filter(title=title).update(editor=user)

        self.stdout.write(
            self.style.SUCCESS(f"Total: {total}, Not found: {not_found}"))

    def create_user(self, email: str) -> User:
        user, created = User.objects.get_or_create(
            username=email,
            email=email,
            defaults={
                "first_name": email.split("@")[0],
                "last_name": "",
            }
        )
        if created:
            user.set_password(get_random_string(16))
            user.save()
            self.stdout.write(self.style.NOTICE(f"User {user} created"))

        return user
