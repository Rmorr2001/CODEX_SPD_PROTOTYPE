from django.core.exceptions import ValidationError

from HOME.models import BannerImage, RushFormLink, RushSlide
from SPDWEBAPP_CORE.testing.base import RegressionTestCase
from SPDWEBAPP_CORE.testing.state import assert_unchanged, snapshot_scope

from .helpers import file_path, image_bytes, slide, upload


class ContentModelTests(RegressionTestCase):
    def sentinels(self, target):
        other = (RushFormLink.objects.create(link="https://example.invalid/keep")
                 if target is BannerImage else BannerImage.objects.create(image=upload()))
        keep = slide("Keep", 2)
        before = snapshot_scope([other, keep], files=[file_path(keep.image)])
        return before

    def value(self, model, suffix="a"):
        return ({"image": upload(f"{suffix}.png", "blue" if suffix == "b" else "red")}
                if model is BannerImage else {"link": f"https://example.invalid/{suffix}"})

    def test_singleton_initial_create_persists_value(self):
        for model in (BannerImage, RushFormLink):
            with self.subTest(model=model.__name__):
                BannerImage.objects.all().delete()
                RushFormLink.objects.all().delete()
                before = self.sentinels(model)
                obj = model.objects.create(**self.value(model))
                obj.refresh_from_db()
                self.assertEqual(model.objects.count(), 1)
                if model is BannerImage:
                    self.assertTrue(obj.image.name.startswith("banners/"))
                    self.assertEqual(file_path(obj.image).read_bytes(), image_bytes())
                    self.assertEqual(str(obj), "Banner Image")
                else:
                    self.assertEqual(obj.link, "https://example.invalid/a")
                    self.assertEqual(str(obj), obj.link)
                assert_unchanged(before)

    def test_successful_singleton_replacement_has_one_new_value(self):
        for model in (BannerImage, RushFormLink):
            with self.subTest(model=model.__name__):
                BannerImage.objects.all().delete()
                RushFormLink.objects.all().delete()
                before = self.sentinels(model)
                old = model.objects.create(**self.value(model))
                replacement = model.objects.create(**self.value(model, "b"))
                self.assertFalse(model.objects.filter(pk=old.pk).exists())
                self.assertEqual(model.objects.count(), 1)
                replacement.refresh_from_db()
                if model is BannerImage:
                    self.assertEqual(file_path(replacement.image).read_bytes(), image_bytes("blue"))
                else:
                    self.assertEqual(replacement.link, "https://example.invalid/b")
                assert_unchanged(before)

    def test_singleton_normal_update_and_repeat_remain_single(self):
        for model in (BannerImage, RushFormLink):
            with self.subTest(model=model.__name__):
                BannerImage.objects.all().delete()
                RushFormLink.objects.all().delete()
                before = self.sentinels(model)
                obj = model.objects.create(**self.value(model))
                for key, value in self.value(model, "b").items():
                    setattr(obj, key, value)
                obj.save()
                obj.save()
                obj.refresh_from_db()
                self.assertEqual(model.objects.count(), 1)
                if model is BannerImage:
                    self.assertEqual(file_path(obj.image).read_bytes(), image_bytes("blue"))
                else:
                    self.assertEqual(obj.link, "https://example.invalid/b")
                assert_unchanged(before)

    def test_model_full_clean_rejects_required_and_length_errors(self):
        old = BannerImage.objects.create(image=upload())
        keep = slide()
        before = snapshot_scope([old, keep], files=[file_path(old.image), file_path(keep.image)])
        variants = [
            (RushFormLink(link=""), "link"), (RushFormLink(link="not-a-url"), "link"),
            (RushFormLink(link="https://example.invalid/" + "x" * (201 - len("https://example.invalid/"))), "link"),
            (RushSlide(caption="", image="synthetic.png"), "caption"),
            (RushSlide(caption="x" * 201, image="synthetic.png"), "caption"),
            (BannerImage(image=""), "image"),
        ]
        for obj, field in variants:
            with self.subTest(model=type(obj).__name__, field=field):
                with self.assertRaises(ValidationError) as error:
                    obj.full_clean()
                self.assertIn(field, error.exception.message_dict)
        assert_unchanged(before)

    def test_slide_create_and_edit_persists_target_fields(self):
        keep = slide("Keep", 2)
        before = snapshot_scope([keep], files=[file_path(keep.image)])
        obj = slide("First", 0)
        obj.caption, obj.order, obj.image = "Changed", 7, upload("new.png", "blue")
        obj.save()
        obj.refresh_from_db()
        self.assertEqual((obj.caption, obj.order, str(obj)), ("Changed", 7, "Changed"))
        self.assertTrue(obj.image.name.startswith("rush_slides/"))
        self.assertEqual(file_path(obj.image).read_bytes(), image_bytes("blue"))
        assert_unchanged(before)

    def test_slide_integer_order_and_caption_boundary(self):
        a, b = slide("x" * 200), slide("Keep", 0)
        before = snapshot_scope([b], files=[file_path(a.image), file_path(b.image)])
        for order in (-1, 0, 2147483647):
            a.order = order
            a.full_clean()
            a.save()
            a.refresh_from_db()
            self.assertEqual((a.order, len(a.caption)), (order, 200))
            self.assertEqual(set(RushSlide.objects.values_list("pk", flat=True)), {a.pk, b.pk})
        assert_unchanged(before)

    def test_slide_row_delete_is_repeatable(self):
        a, b = slide("Remove"), slide("Keep")
        before = snapshot_scope([b], files=[file_path(b.image)])
        pk = a.pk
        self.assertEqual(RushSlide.objects.filter(pk=pk).delete()[0], 1)
        self.assertEqual(RushSlide.objects.filter(pk=pk).delete()[0], 0)
        self.assertFalse(RushSlide.objects.filter(pk=pk).exists())
        assert_unchanged(before)
