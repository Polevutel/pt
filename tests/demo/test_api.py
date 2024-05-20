import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from model_bakery import baker

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def course_factory():
    def create_course(**kwargs):
        return baker.make('courses.Course', **kwargs)
    return create_course

@pytest.fixture
def student_factory():
    def create_student(**kwargs):
        return baker.make('students.Student', **kwargs)
    return create_student
@pytest.mark.django_db
def test_retrieve_course(api_client, course_factory):
    # Создаём курс через фабрику
    course = course_factory()

    # Строим URL и делаем запрос через тестовый клиент
    url = reverse('courses-detail', args=[course.id])
    response = api_client.get(url)

    # Проверяем, что вернулся именно тот курс, который запрашивали
    assert response.status_code == 200
    assert response.data['id'] == course.id
    assert response.data['name'] == course.name


@pytest.mark.django_db
def test_list_courses(api_client, course_factory):
    # Создаём несколько курсов через фабрику
    courses = course_factory(_quantity=3)

    # Делаем запрос и проверяем результат
    url = reverse('courses-list')
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 3
    assert all(c['id'] in [course.id for course in courses] for c in response.data)


@pytest.mark.django_db
def test_filter_courses_by_id(api_client, course_factory):
    # Создаём несколько курсов через фабрику
    courses = course_factory(_quantity=3)

    # Фильтруем по ID одного из курсов
    url = reverse('courses-list')
    response = api_client.get(url, {'id': courses[0].id})
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['id'] == courses[0].id


@pytest.mark.django_db
def test_filter_courses_by_name(api_client, course_factory):
    # Создаём несколько курсов через фабрику
    course_factory(name='Course 1')
    course_factory(name='Course 2')
    course_factory(name='Course 3')

    # Фильтруем по названию
    url = reverse('courses-list')
    response = api_client.get(url, {'name': 'Course 2'})
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'Course 2'


@pytest.mark.django_db
def test_create_course(api_client):
    # Готовим JSON-данные и создаём курс
    data = {'name': 'New Course'}
    url = reverse('courses-list')
    response = api_client.post(url, data, format='json')

    # Проверяем, что курс был создан
    assert response.status_code == 201
    assert response.data['name'] == 'New Course'


@pytest.mark.django_db
def test_update_course(api_client, course_factory):
    # Создаём курс через фабрику
    course = course_factory()

    # Обновляем курс через API
    data = {'name': 'Updated Course'}
    url = reverse('courses-detail', args=[course.id])
    response = api_client.put(url, data, format='json')

    # Проверяем, что курс был обновлен
    assert response.status_code == 200
    assert