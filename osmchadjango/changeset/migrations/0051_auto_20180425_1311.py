# Generated by Django 2.0.3 on 2018-04-25 13:11
import json

from django.db import migrations, transaction


def filtered_json(feature):
    PRIMARY_TAGS = [
        'aerialway',
        'aeroway',
        'amenity',
        'barrier',
        'boundary',
        'building',
        'craft',
        'emergency',
        'geological',
        'highway',
        'historic',
        'landuse',
        'leisure',
        'man_made',
        'military',
        'natural',
        'office',
        'place',
        'power',
        'public_transport',
        'railway',
        'route',
        'shop',
        'tourism',
        'waterway'
    ]
    data = {
        "osm_id": feature.osm_id,
        "url": "{}-{}".format(feature.osm_type, feature.osm_id),
        "version": feature.osm_version,
        "reasons": [reason.id for reason in feature.reasons.all()]
    }


    if 'properties' in json.loads(feature.geojson).keys():
        properties = json.loads(feature.geojson)['properties']
        if 'name' in properties.keys():
            data['name'] = properties['name']

        [
            properties.pop(key) for key in list(properties.keys())
            if key not in PRIMARY_TAGS
        ]
        data['primary_tags'] = properties

    return data


def migrate_features(apps, schema_editor):
    Changeset = apps.get_model('changeset', 'Changeset')
    changesets = Changeset.objects.filter(
        features__isnull=False
        ).prefetch_related('features').order_by('id')
    changeset_count = changesets.count()
    migrated = 0
    print('{} changesets to migrate'.format(changesets.count()))
    while migrated < changeset_count:
        with transaction.atomic():
            for changeset in changesets[migrated:migrated + 1000]:
                new_features_data = [
                    filtered_json(feature) for feature in changeset.features.all()
                    ]
                changeset.new_features = new_features_data
                changeset.save(update_fields=['new_features'])
        print('{}-{} changesets migrated'.format(migrated, migrated + 1000))
        migrated += 1000


class Migration(migrations.Migration):
    atomic = False
    dependencies = [
        ('changeset', '0050_changeset_new_features'),
        ('feature', '0016_auto_20180307_1417')
    ]

    operations = [
        migrations.RunPython(
            migrate_features, reverse_code=migrations.RunPython.noop
        ),
    ]
