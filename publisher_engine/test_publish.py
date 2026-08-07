from builder import PublisherBuilder

builder = PublisherBuilder()

result = builder.publish(

    build_root="/volume1/docker/curriculum-builder/builds/2026/07",

    build_name="BLD_20260716_000115_English_FoundationYear_Language",

    lesson_package_id="LP_000115_001"

)

print(result)