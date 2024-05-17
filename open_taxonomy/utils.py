from openai import OpenAI

client = OpenAI()
import math
from textwrap import dedent

async def is_node_relevant(query, node_name):
    instructions = dedent(f"""
    You are classifying products against a hierarchical taxonomy tree. Given a product description (query) and a taxonomy node (node name), you need to determine whether the node is relevant to the product. 
    If a node is relevant, we will further explore the node's children to refine the classification.
    Given a product description and a taxonomy node, decide if the node is relevant to the product.

    Return TRUE if the node is relevant to the product description, and FALSE otherwise.

    Product Description: HP Newest 14" Ultral Light Laptop for Students and Business, Intel Quad-Core N4120, 8GB RAM, 192GB Storage(64GB eMMC+128GB Micro SD), 1 Year Office 365, Webcam, HDMI, WiFi, USB-A&C, Win 11 S
    Taxonomy Node: Home & Garden
    Remember, only return TRUE or FALSE!
    Response: FALSE
    """)

    prompt = dedent(f"""
    Query: {query}
    Node: {node_name}
    Remember, only return TRUE or FALSE!
    Response: """)

    template = dedent(f"""
    <|im_start|>system
    {instructions}
    <|im_end|>
    <|im_start|>user
    {prompt}
    <|im_end|>
    """)

    response = client.completions.create(
        model="gpt-4o",
        prompt=template,
        max_tokens=100,
        temperature=0.1,
        logprobs=1,
        stop=["<|im_end|>"]
    )
    message = response.choices[0].text.strip()
    logprobs = response.choices[0].logprobs.top_logprobs[0]
    confidence = sum(math.exp(logprob) for logprob in logprobs.values())


    # chatcompletions version 
    # response = client.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "system", "content": instructions},
    #         {"role": "user", "content": prompt}
    #     ],
    #     max_tokens=100,
    #     temperature=0.1,
    #     logprobs=1,
    #     stop=["\n"]
    # )
    # message = response.choices[0].message.content
    # logprobs = response.choices[0].message.logprobs.top_logprobs[0]
    # confidence = sum(math.exp(logprob) for logprob in logprobs.values())
    # print(f"LLM Response: {message}, Confidence: {confidence}")
    if "Response:" in message:
        message = message.split("Response:")[1].strip()
    return { "message": message, "confidence": confidence }
