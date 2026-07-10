# core/services/course_service.py

from core.models import Course

class CourseService:

    @staticmethod
    def get_all(search=None):
        queryset = Course.objects.filter(is_active=True).select_related('department')

        if search:
            queryset = queryset.filter(coursename__icontains=search)

        return queryset.order_by('-created_at')

    @staticmethod
    def create(data):
        course = Course.objects.create(
            coursename=data.get("coursename"),
            department_id=data.get("department"),
            is_active=True
        )

        # ManyToMany interests
        interest_ids = data.getlist("interests")
        if interest_ids:
            course.interests.set(interest_ids)

        return course

    @staticmethod
    def update(course_id, data):
        course = Course.objects.get(id=course_id)

        course.coursename = data.get("coursename")
        course.department_id = data.get("department")
        course.save()

        interest_ids = data.getlist("interests")
        if interest_ids:
            course.interests.set(interest_ids)
        else:
            course.interests.clear()

        return course

    @staticmethod
    def delete(course_id):
        course = Course.objects.get(id=course_id)
        course.is_active = False
        course.save()