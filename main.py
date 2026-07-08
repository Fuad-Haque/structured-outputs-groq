import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Point the official OpenAI SDK at Groq's OpenAI-compatible endpoint.
# This one line is the entire "free-tier substitution" — everything else
# below is standard OpenAI SDK usage and will work unchanged against
# api.openai.com if you ever swap providers.
client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "openai/gpt-oss-20b"  # confirmed strict:true support on Groq as of this build

# The schema. Every property in `properties` MUST also appear in `required`
# per Groq's strict-mode compiler rule (Section 2) — this is NOT optional
# the way it is on OpenAI's own API.
PRODUCT_REVIEW_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "product_review",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "product_name": {"type": "string"},
                "rating": {"type": "number"},
                "sentiment": {
                    "type": "string",
                    "enum": ["positive", "negative", "neutral"],
                },
                "key_features": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["product_name", "rating", "sentiment", "key_features"],
            "additionalProperties": False,
        },
    },
}


def extract_review(raw_text: str) -> dict:
    """
    Sends one unstructured text blob through the schema-constrained call.
    Returns a parsed dict guaranteed (under strict mode, on a supported
    model) to match PRODUCT_REVIEW_SCHEMA exactly.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "Extract product review information from the text.",
            },
            {"role": "user", "content": raw_text},
        ],
        response_format=PRODUCT_REVIEW_SCHEMA,
    )

    # This is the part that would normally need a try/except around
    # json.loads() with free-text output. Under strict mode, this line
    # is not supposed to be able to throw — that guarantee is the entire
    # point of the concept, and Step 4 exists to test whether it holds.
    content = response.choices[0].message.content
    return json.loads(content)


# Ten deliberately messy, real-world-shaped inputs — different lengths,
# different tones, one with no rating stated, one that's mostly complaints,
# one that's a single sentence, one that's a rambling paragraph.
TEST_INPUTS = [
    "I bought the UltraSound Headphones last week and I'm really impressed! The noise cancellation is amazing and the battery lasts all day. Sound quality is crisp and clear. I'd give it 4.5 out of 5 stars.",
    "Absolute trash. The StreamCam 4K disconnected constantly, the app crashed twice a day, and customer support never replied. 1 star, would not recommend to anyone.",
    "It's fine I guess. The GripFit Water Bottle keeps things cold for a while but the lid leaks a little if you tip it sideways. 3/5.",
    "Just got the NightOwl Desk Lamp. Three brightness settings, USB charging port built in, and it looks great on my desk. Haven't had it long enough to judge durability yet but so far so good, probably a 4.",
    "Worst purchase I've made this year. The FlexBand Fitness Tracker's heart rate sensor is wildly inaccurate, the strap broke after nine days, and the companion app drains my phone battery. Zero stars if that were an option.",
    "The AeroPress clone I bought works exactly like the real thing for a third of the price. Great build quality, easy to clean, makes excellent coffee. Five stars, no notes.",
    "Mixed feelings on this one. The QuietType Mechanical Keyboard sounds fantastic and the keys feel premium, but two keys already feel a bit mushy after light use. Middle of the road, 3 stars.",
    "This blender exceeded every expectation I had going in. The PowerBlend Pro chews through frozen fruit and ice like it's nothing, cleanup takes ten seconds, and it's whisper quiet compared to my old one. Easily 5 stars.",
    "Returned it. The SolarCharge Power Bank took over six hours to charge my phone from empty, which defeats the entire purpose of a solar charger. Not usable.",
    "Decent budget option. The ClipLight Book Light has a weak clip that slips off thicker hardcovers, but the light itself is bright and has good battery life. I'd call it a 3, works for the price.",
]

if __name__ == "__main__":
    for i, text in enumerate(TEST_INPUTS, start=1):
        result = extract_review(text)
        print(f"--- Input {i} ---")
        print(json.dumps(result, indent=2))
        print()