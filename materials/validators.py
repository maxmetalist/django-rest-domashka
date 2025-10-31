from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class YouTubeURLValidator:
    """
    Валидатор для проверки ссылок на сторонние ресурсы.
    Разрешает только ссылки на youtube.com
    """

    def __call__(self, value):
        if not value:
            return  # Пустые значения разрешены

        # Проверяем, является ли значение строкой
        if not isinstance(value, str):
            raise ValidationError(_("Ссылка должна быть строкой"))

        # Проверяем, что значение начинается с http:// или https://
        if not value.startswith(("http://", "https://")):
            raise ValidationError(_("Ссылка должна начинаться с http:// или https://"))

        try:
            parsed_url = urlparse(value)
            domain = parsed_url.netloc.lower()

            # Разрешенные домены
            allowed_domains = ["youtube.com", "www.youtube.com", "youtu.be"]

            # Проверяем домен
            is_valid = any(allowed_domain in domain for allowed_domain in allowed_domains)

            if not is_valid:
                raise ValidationError(
                    _("Ссылки разрешены только на YouTube. А вот это: %(domain)s хрень какая-то"),
                    params={"domain": domain},
                    code="invalid_domain",
                )

        except Exception as e:
            raise ValidationError(_("Некорректный формат ссылки: %(error)s") % {"error": str(e)})


# Создаем экземпляр валидатора для использования в сериализаторах
youtube_url_validator = YouTubeURLValidator()
