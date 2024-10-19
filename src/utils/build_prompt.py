# Fixed version of question content formatting in the OpenToMPromptBuilder class
class OpenToMPromptBuilder:

    @staticmethod
    def simple_entity_state(
        mover: str, 
        affected_char: str, 
        eoi: str, 
        question_content: str, 
        question_content_tokens: list, 
        cur_narrative: str, 
        entity_state_prompt_template: str,
        cot: bool,
        cot_postfix: str = '',
        simtom_template: str = '',
    ):
        # Rest of the method remains unchanged until question_content formatting
        coi = ''
        second_order_statement = ''
        if mover in question_content and affected_char in question_content:
            if question_content_tokens.index(mover) < question_content_tokens.index(affected_char):
                coi = mover 
                second_order_statement = f" {affected_char} will think that"
            else:
                coi = affected_char 
                second_order_statement = f" {mover} will think that"
        elif mover in question_content:
            coi = mover
        elif affected_char in question_content:
            coi = affected_char  
        else:
            coi = 'the narrator'

        # Add Yes/No qualifier for location questions
        if 'locate' in question_content:
            question_content = f"{question_content} Answer with 'Yes' or 'No'."

        cur_prompt = entity_state_prompt_template.replace('{narrative}', cur_narrative) \
            .replace('{question}', question_content) \
            .replace('{eoi}', eoi) \
            .replace('{coi}', coi) \
            .replace('{second_order_statement}', second_order_statement)

        if cot:
            if 'initial' in question_content:
                cur_prompt = '.'.join(cur_prompt.split('.')[:-2]) + '. ' + cot_postfix
            else:
                cur_prompt = cur_prompt.split('?')[0] + '? ' + cot_postfix

        if simtom_template:
            cur_prompt = simtom_template.replace('{narrative}', cur_narrative) \
                .replace('{coi}', coi) \
                .replace('{eoi}', eoi) \
                .replace('{coi-events}', cur_narrative.strip()) \
                .replace('{question}', question_content) \
                .split('Options:')[0].strip()

        return cur_prompt.strip(), coi

    @staticmethod
    def fullness(
        original_place: str,
        move_to_place: str,
        mover: str,
        affected_char: str,
        question_content: str, 
        question_content_tokens: list,
        cur_narrative: str,
        multihop_fullness_prompt_template: str,
        cot: bool,
        cot_postfix: str='',
        simtom_template: str='',
    ):
        # Rest of the method remains unchanged until question formatting 
        poi = ''
        if original_place in question_content:
            poi = original_place
        elif move_to_place in question_content:
            poi = move_to_place

        coi = ''
        second_order_statement = ''
        if mover in question_content and affected_char in question_content:
            if question_content_tokens.index(mover) < question_content_tokens.index(affected_char):
                coi = mover
                second_order_statement = f" {affected_char} will think that"
            else:
                coi = affected_char
                second_order_statement = f" {mover} will think that"
        elif mover in question_content:
            coi = mover
        elif affected_char in question_content:
            coi = affected_char  
        else:
            coi = 'the narrator'

        # Add fullness qualifier
        question_content = f"{question_content} Answer with 'more full', 'equally full', or 'less full'."

        cur_prompt = multihop_fullness_prompt_template.replace('{narrative}', cur_narrative) \
            .replace('{question}', question_content) \
            .replace('{poi}', poi) \
            .replace('{coi}', coi) \
            .replace('{second_order_statement}', second_order_statement)

        if cot:
            cur_prompt = '.'.join(cur_prompt.split('.')[:-2]) + '. ' + cot_postfix

        if simtom_template:
            cur_prompt = simtom_template.replace('{narrative}', cur_narrative) \
                .replace('{coi}', coi) \
                .replace('{poi}', poi) \
                .replace('{coi-events}', cur_narrative.strip()) \
                .replace('{question}', question_content) \
                .split('Options:')[0].strip()

        return cur_prompt, coi

    @staticmethod
    def accessibility(
        mover: str,
        affected_char: str,
        eoi: str,
        question_content: str,
        question_content_tokens: list,
        cur_narrative: str,
        multihop_accessibility_prompt_template: str,
        cot: bool,
        cot_postfix: str='',
        simtom_template: str='',
    ):
        coi = ''
        if mover in question_content:
            coi = mover
        elif affected_char in question_content:
            coi = affected_char  
        else:
            coi = 'the narrator'

        second_order_statement = ''
        if mover in question_content and affected_char in question_content:
            second_order_statement = f" for {affected_char},"

        # Add accessibility qualifier
        question_content = f"{question_content} Answer with 'more accessible', 'equally accessible', or 'less accessible'."

        cur_prompt = multihop_accessibility_prompt_template.replace('{narrative}', cur_narrative) \
            .replace('{question}', question_content) \
            .replace('{eoi}', eoi) \
            .replace('{coi}', coi) \
            .replace('{second_order_statement}', second_order_statement)

        if cot:
            cur_prompt = '.'.join(cur_prompt.split('.')[:-2]) + '. ' + cot_postfix

        if simtom_template:
            cur_prompt = simtom_template.replace('{narrative}', cur_narrative) \
                .replace('{coi}', coi) \
                .replace('{coi-events}', cur_narrative.strip()) \
                .replace('{question}', question_content) \
                .replace('{eoi}', eoi) \
                .split('Options:')[0].strip()

        return cur_prompt, coi

    @staticmethod
    def attitude(
        attitude_prompt_template: str, 
        mover: str,
        affected_char: str,
        cur_narrative: str, 
        question_content: str, 
        cot: bool,
        cot_postfix: str='',
        simtom_template: str='',
        high_level_attitude: bool = False,
        ac_preference: str = '',
    ):
        # Add attitude qualifier
        question_content = question_content.split('?')[0].strip() + ', assuming that you observed the action? Answer with "positive", "neutral", or "negative".'

        if high_level_attitude:
            assert ac_preference != '', 'must provide observer(ac)\'s preference when using high-level abstraction'
            
            main_event = question_content.split('towards')[-1] \
                .split(',')[0] \
                .replace("'s action of", '') \
                .replace("moving", "moves") \
                .strip() + '.'

            new_narrative = ac_preference + ' ' + main_event
            new_question = f"As {affected_char}, what is your attitude towards {mover}'s action? Answer with \"positive\", \"neutral\", or \"negative\"."
            cur_prompt = attitude_prompt_template.replace('{narrative}', new_narrative).replace('{question}', new_question)
        else:
            cur_prompt = attitude_prompt_template.replace('{narrative}', cur_narrative).replace('{question}', question_content)

        if cot:
            cur_prompt = cur_prompt.strip() + ' ' + cot_postfix.strip()
        else:
            cur_prompt = cur_prompt.strip() + ' Answer without any explanation.'

        if simtom_template:
            cur_prompt = simtom_template.replace('{narrative}', cur_narrative) \
                .replace('{coi}', affected_char) \
                .replace('{coi-events}', cur_narrative.strip()) \
                .replace('{question}', question_content) \
                .split('Options:')[0].strip()

        return cur_prompt, affected_char

    @staticmethod
    def preference(
        mover: str,
        affected_char: str,
        eoi: str,
        cur_narrative: str,
        question_content: str,
        preference_prompt_template: str,
        cot: bool,
        cot_postfix: str='',
        simtom_template: str='',
    ):
        coi = ''
        if mover in question_content:
            coi = mover
        else:
            coi = affected_char

        # Add Yes/No qualifier for preference questions
        question_content = f"{question_content} Answer with 'Yes' or 'No'."

        cur_prompt = preference_prompt_template.replace('{narrative}', cur_narrative) \
            .replace('{coi}', coi) \
            .replace('{eoi}', eoi) \
            .replace('{question}', question_content)

        if cot:
            cur_prompt = '.'.join(cur_prompt.split('.')[:-2]) + '. ' + cot_postfix

        if simtom_template:
            cur_prompt = simtom_template.replace('{narrative}', cur_narrative) \
                .replace('{coi}', coi) \
                .replace('{eoi}', eoi) \
                .replace('{coi-events}', cur_narrative.strip()) \
                .replace('{question}', question_content) \
                .split('Options:')[0].strip()

        return cur_prompt, coi

    @staticmethod
    def intention(
        cur_narrative: str, 
        mover: str,
        question_content: str, 
        question_dict: dict, 
        intention_prompt_template: str, 
        cot: bool,
        cot_postfix: str='',
        simtom_template: str='',
    ):
        # For intention questions, add the options from question_dict
        cur_prompt = intention_prompt_template.replace('{narrative}', cur_narrative) \
            .replace('{question}', question_content) \
            .replace('{options}', question_dict['options'])

        if cot:
            cur_prompt, options = cur_prompt.split('Options:')
            cur_prompt = '.'.join(cur_prompt.split('?')[:-1]) + '? ' + cot_postfix
            cur_prompt += '\nOptions:' + options

        if simtom_template:
            cur_prompt = simtom_template.replace('{narrative}', cur_narrative) \
                .replace('{coi}', mover) \
                .replace('{coi-events}', cur_narrative.strip()) \
                .replace('{question}', question_content) \
                .replace('{options}', question_dict['options'])

        return cur_prompt, mover
