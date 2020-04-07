import pytest

from thepups_workflow.process_dog_report import app


@pytest.fixture()
def file_load_s3_event():
    """ Generates API GW Event"""

    return {
        "Records": [
            {
                "eventVersion": "2.0",
                "eventSource": "aws:s3",
                "awsRegion": "{region}",
                "eventTime": "1970-01-01T00:00:00Z",
                "eventName": "ObjectCreated:Put",
                "userIdentity": {
                    "principalId": "EXAMPLE"
                },
                "requestParameters": {
                    "sourceIPAddress": "127.0.0.1"
                },
                "responseElements": {
                    "x-amz-request-id": "EXAMPLE123456789",
                    "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH"
                },
                "s3": {
                    "s3SchemaVersion": "1.0",
                    "configurationId": "testConfigRule",
                    "bucket": {
                        "name": "sourcebucket",
                        "ownerIdentity": {
                            "principalId": "EXAMPLE"
                        },
                        "arn": "arn:{partition}:s3:::mybucket"
                    },
                    "object": {
                        "key": "HappyFace.jpg",
                        "size": 1024,
                        "eTag": "0123456789abcdef0123456789abcdef",
                        "sequencer": "0A1B2C3D4E5F678901"
                    }
                }
            }
        ]
    }


# def test_lambda_handler(file_load_s3_event, mocker):
#     ret = app.lambda_handler(file_load_s3_event, "")
#     data = json.loads(ret["body"])
#
#     assert ret["statusCode"] == 200
#     assert "message" in ret["body"]
#     assert data["message"] == "hello world"
#     worldassert "location" in data.dict_keys()


# Test Age to Months
age_test_data = [
    ('SF/00y 03m', 3),
    ('NM/05y 00m', 60),
    ('NM/00m', 0),  # Bad Data
    ('M/10y 02m', 122)
]


@pytest.mark.parametrize("input_text, expected_months", age_test_data)
def test_get_age_in_months(input_text, expected_months):
    age = app.get_age_in_months(input_text)
    assert age == expected_months


# Test Name Extraction
name_test_data = [
    ('Wilbert - Adoption pendin. Pomeranian/Mix', 'Wilbert'),
    ('Yogi Bear Great Dane/Mix', 'Yogi Bear Great Dane/Mix'),
    ('Miso Bulldog, American/Mix', 'Miso Bulldog'),
    ('Manning Mixed Breed, Medium (up to 44 lbs fully grown)/Mix', 'Manning Mixed Breed'),
    ('Hazel Australian Cattle Dog/Mix', 'Hazel Australian Cattle Dog/Mix'),
    ('Prancy Clancy Retriever, Labrador/Mix', 'Prancy Clancy Retriever'),
    ('Aster-Pending Adoption Chihuahua', 'Aster'),
    ('T-Rex Retriever, Labrador/Basset Hound', 'T-Rex Retriever')
]


@pytest.mark.parametrize("input_text, expected_name", name_test_data)
def test_get_name(input_text, expected_name):
    age = app.get_name(input_text)
    assert age == expected_name


# Test Age to Months
weight_test_data = [
    ('', 0),
    ('  ', 0),
    ('40 lb', 40),
    ('50', 50),
    ('bad data', 0)  # Bad Data
]


@pytest.mark.parametrize("input_text, expected_weight", weight_test_data)
def test_get_weight(input_text, expected_weight):
    age = app.get_weight(input_text)
    assert age == expected_weight


level_test_data = [
    (
        ["", "", "", "", "Blue - Intermediate",
         "Big guy, pulls so hard he chokes himself, mild RG toward other dogs&nbsp;",
         ""], 'Blue'),
    (["", "", "", "", "Green - All", "", "", "", ""], 'Green'),
    (["", "", "", "", "Purple - Advanced", "MUST READ PLAN.&nbsp;", "", "", ""], 'Purple'),
    (["", "", "", "", "Purple - Advanced", "", "", "", ""], 'Purple'),
    (["", "", "", "", "Red - Designated Handlers Only", "", "", "", ""], 'Red'),
    (["", "", "", "", "Red - Designated Handlers Only", "BQ staff only - until 5pm on 2/26", "", "", ""], 'Red'),
    (["", "", "", "", "Orange - Puppy/Kitten", "", "", "", ""], 'Orange'),
    (["", "", "", "", "Orange - Puppy/Kitten", ". Wear Gown and Gloves.", "", "", ""], 'Orange'),
    (["", "", "", "", "Red - Designated Handlers Only", "TEAM RONNIE", "", "", ""], 'Red - Team'),
    (["", "", "", "", "Not a level", "TEAM RONNIE", "", "", ""], None),
]


@pytest.mark.parametrize("input_text, expected_level", level_test_data)
def test_get_weight(input_text, expected_level):
    age = app.get_level(input_text)
    assert age == expected_level
