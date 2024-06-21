import instructor
from openai import OpenAI

import math
from textwrap import dedent
from .taxonomy_category import TaxonomyCategory
from pydantic import BaseModel

async def is_node_relevant(query, node_name, node_description=""):
    client = OpenAI()
    instructions = dedent(f"""\
    You are classifying a single product against a hierarchical taxonomy tree. Given a product description and a node in the taxonomy, you need to determine whether the node is improves the classification or not. 
    If a node improves the classification, we will further explore the node's children to refine our results.
    Given a product description and a taxonomy node, decide if the node is a correct classification for the product description.

    Return TRUE if the node is a correct classification for the product description, and FALSE if it is not.
                          
    Tips: 
    - Never label Uncategorized.
    - If there are components listed in the product description, only classify the product itself.
    - It is important not to explore nodes where children are not likely to contain relevant categories.""")

    example = dedent(f"""\
    Product Description: HP Newest 14" Ultral Light Laptop for Students and Business, Intel Quad-Core N4120, 8GB RAM, 192GB Storage(64GB eMMC+128GB Micro SD), 1 Year Office 365, Webcam, HDMI, WiFi, USB-A&C, Win 11 S
    Node: Home & Garden
    Node Description: This category includes products related to home and garden.
    Remember, only return TRUE or FALSE!
    Response: """)

    prompt = dedent(f"""\
    Product Description: {query}
    Node: {node_name}
    Node Description: {node_description}
    Remember, only return TRUE or FALSE!
    Response: """)

    # print(prompt)

    chatml_template = dedent(f"""\
    <|im_start|>system
    {instructions}
    <|im_end|>
    <|im_start|>user
    {example}
    <|im_end|>
    <|im_start|>assistant
    FALSE
    <|im_end|>
    <|im_start|>user
    {prompt}
    <|im_end|>
    <|im_start|>assistant
    """)

    instruct_template = dedent(f"""<s>[INST] {instructions} {example} [/INST] FALSE</s> [INST] {prompt} [/INST]""")
    # print(instruct_template)
    response = client.completions.create(
        model="davinci-002",
        prompt=chatml_template,
        max_tokens=100,
        temperature=0.1,
        logprobs=1,
        stop=["</s>", "[INST]", "<|im_end|>"]
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


    