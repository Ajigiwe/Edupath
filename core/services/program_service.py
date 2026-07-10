from core.models import Program
from django.shortcuts import get_object_or_404


class ProgramService:

    @staticmethod
    def get_all(search=None):
        queryset = Program.objects.filter(is_active=True)

        if search:
            queryset = queryset.filter(programname__icontains=search)

        return queryset.order_by('-created_at')

    @staticmethod
    def create(data):
        program = Program.objects.create(
            programname=data.get("title"),
            is_active=True
        )

        interest_ids = data.getlist("interests")

        if interest_ids:
            program.interests.set(interest_ids)

        return program

    @staticmethod
    def update(program_id, data):
        program = get_object_or_404(Program, id=program_id)

        program.programname = data.get("title")
        program.save()

        interest_ids = data.getlist("interests")

        if interest_ids:
            program.interests.set(interest_ids)
        else:
            program.interests.clear()

        return program

    @staticmethod
    def delete(program_id):
        program = Program.objects.get(id=program_id)
        program.is_active = False
        program.save()
