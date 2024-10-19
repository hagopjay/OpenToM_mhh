#%%writefile run_booster.py

import sys, os
import random
import argparse
from tqdm import tqdm
import numpy as np
from typing import Dict, List, Tuple
import json


class DataUtils:
    @staticmethod
    def load_json(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)


def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)


def sample_entries(meta_data: dict, batch_size: int = 50):
    keys = list(meta_data.keys())
    random.shuffle(keys)
    for i in range(0, len(keys), batch_size):
        yield keys[i:i+batch_size]


pre_prompt = f"Please perform a meticulous, precise and highly detailed analysis of the provided narrative using the following guidelines: 1. Assemble a Timeline: Construct a clear, step-by-step timeline of the conversation and actions, noting any points where a character, subject or object enters, leaves, or returns to the narrative or conversation. Keep track of subject's and object's states of accessibility and inaccessibility, along with emotion and sentiments expressed. 2. Meticulous Tracking of Explicit Perceptions: - Identify and document each character's explicit Perceptions based only on what they directly hear, see, or experience in the narrative. - Do not assume a character knows something unless it has been explicitly mentioned or shown in the text that the character has directly experienced it. 3. Do Not Assume Inferences: - Avoid assuming that a character infers information unless the narrative provides clear and explicit evidence that the character made an inference. - If an inference is made within the text, explain what evidence led to this conclusion. 4. Theory of Mind (ToM) Application: - Apply the principles of Theory of Mind, ensuring that each character's knowledge and beliefs are based strictly on their Perceptions and interactions within the timeline. - Track whether each character is aware of what others know or believe based on their direct interaction. 5. Webb Equation of Emotion and Mind Hacking Happiness Framework: - Use these frameworks to explain emotional responses, focusing on how characters' expectations (EPs) and perceptions (P) interact within the narrative. - Account for any emotional reactions that result from mismatched EPs and P. Please ensure that this methodology is followed closely for each part of the narrative.  Please ensure that this methodology is followed closely for each part of the narrative.  You will be asked questions based on this narrative and many of the questions are meant to trick you into answering imprecisely. Please answer precisely, without ever inferring. If an answer is only partially or likely correct, the answer will probably be negative. Please keep your answer as terse as possible. Often the answer will only require a few words."

def build_combined_prompt(key: str, narrative: str, questions: List[Dict]) -> str:
    prompt = f"Key: {key} | {pre_prompt} Narrative: {narrative} | Questions: "
    for i, q_dict in enumerate(questions, 1):
        prompt += f"Question {i}: {q_dict['question']} | "
    return prompt.strip()



def get_result(key: str, val: dict, all_questions: dict, valid_q_types: list) -> Tuple[str, List[Dict]]:
    narrative = val['long_narrative'] if args.long_narrative else val['narrative']
    
    questions = []
    ground_truth = []
    
    for q_type in valid_q_types:
        if key in all_questions[q_type]:
            type_questions = all_questions[q_type][key]
            for q in type_questions:
                questions.append({
                    'question': q['question'],
                    'type': q_type
                })
                ground_truth.append({
                    'answer': q['answer'],
                    'type': q_type
                })
    
    combined_prompt = build_combined_prompt(key, narrative, questions)
    
    with open('PromptOutBatching.txt', 'a') as f:
        f.write(f"\n{'='*80}\n")
        f.write(f"Narrative Key: {key}\n")
        f.write(combined_prompt)
        f.write("\n\nGround Truth:\n")
        for i, truth in enumerate(ground_truth, 1):
            f.write(f"Answer {i}: {truth['answer']} (Type: {truth['type']})\n")
        f.write(f"\n{'='*80}\n")
    
    # Print the prompt to console in a single line with double quotes and comma
    console_prompt = combined_prompt.replace('"', "'").replace('\n', ' ')  # Replace double quotes and newlines
    print(f'"{console_prompt}",')
    
    return combined_prompt, ground_truth



def evaluate_responses(responses: List[str], ground_truth: List[Dict]) -> Dict:
    results = {
        'total_questions': len(ground_truth),
        'correct': 0,
        'incorrect': 0,
        'scores_by_type': {}
    }
    
    for resp, truth in zip(responses, ground_truth):
        clean_resp = resp.strip().lower()
        clean_truth = str(truth['answer']).strip().lower()
        
        q_type = truth['type']
        if q_type not in results['scores_by_type']:
            results['scores_by_type'][q_type] = {
                'total': 0,
                'correct': 0
            }
        
        results['scores_by_type'][q_type]['total'] += 1
        
        if clean_resp == clean_truth:
            results['correct'] += 1
            results['scores_by_type'][q_type]['correct'] += 1
        else:
            results['incorrect'] += 1
            
    results['overall_accuracy'] = results['correct'] / results['total_questions']
    for q_type in results['scores_by_type']:
        type_stats = results['scores_by_type'][q_type]
        type_stats['accuracy'] = type_stats['correct'] / type_stats['total']
        
    return results



def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--question_type', type=str, default='all', nargs='+', help='choose which question type to evaluate, use "all" for all questions')
    parser.add_argument('--long_narrative', action='store_true', default=False, help='whether to evaluate on long narrative')
    parser.add_argument('--num_batch', type=int, default=5, help='number of batches to evaluate')
    parser.add_argument('--seed', type=int, default=42, help='random seed')
    parser.add_argument('--batch_size', type=int, default=50, help='batch size for evaluation')
    return parser.parse_args()





def main():
    global args
    args = get_args()
    set_seed(args.seed)

    # Load meta_data
    if args.long_narrative:
        meta_data = DataUtils.load_json('../data/opentom_data/meta_data_long.json')
    else:
        meta_data = DataUtils.load_json('../data/opentom_data/meta_data.json')

    valid_q_types = ['location_cg_fo', 'location_cg_so', 'multihop_fo', 'multihop_so', 'attitude']
    
    all_questions = {}
    for q_type in valid_q_types:
        all_questions[q_type] = DataUtils.load_json(f'../data/opentom_data/{q_type}.json')

    # Clear the output file at the start of each run
    open('PromptOutBatching.txt', 'w').close()

    for batch in range(args.num_batch):
        for key_list in sample_entries(meta_data, batch_size=args.batch_size):
            for key in key_list:
                val = meta_data[key]
                prompt, ground_truth = get_result(key, val, all_questions, valid_q_types)
                
                # Here you would make your API call to the LLM
                # responses = llm_api_call(prompt)
                
                # For demonstration, just print the number of questions
                #print(f"Generated prompt for narrative {key} with {len(ground_truth)} questions\n\n")
                
                # If you implement the API call, you can evaluate responses like this:
                # eval_results = evaluate_responses(responses, ground_truth)
                # print(f"Evaluation results for narrative {key}: {eval_results}")

if __name__ == '__main__':
    main()
