#!/usr/bin/env python

# person: first, second, third
# number: singular, plural
# voice: active, passive
# tense: past, present, future,
# aspect: unmarked, progressive, perfect


import re
import irregulars

CONSONANTS = list('bcdfghjklmnpqrstvwxz')
DOUBLED_CONSONANTS = list('bcdfghjklmnpqrstz')
VOWELS = list('aeiouy')
CONSONANTS_PATTERN = "[" + ''.join(CONSONANTS) + "]"
DOUBLED_CONSONANTS_PATTERN = "[" + ''.join(DOUBLED_CONSONANTS) + "]"
VOWELS_PATTERN = "[" + ''.join(VOWELS) + "]"
FORMS = {}


def construct_forms():
    global FORMS
    if FORMS != {}:
        return FORMS

    forms = {}
    for vv in ['active', 'passive']:
        forms[vv] = {}

    forms['active']['unmarked'] = [':verb']
    forms['active']['progressive'] = [':be', ':present_participle']
    forms['active']['perfect'] = [':have', ':past_participle']
    forms['passive']['unmarked'] = [':be', ':past_participle']
    forms['passive']['progressive'] = [':be', 'being', ':past_participle']
    forms['passive']['perfect'] = [':have', 'been', ':past_participle']

    # TODO:  future perfect passive progressive
    # I will have been being released

    FORMS = forms
    return FORMS


def conjugate(infinitive='be', person='third', number='singular',
              voice='active', tense='present', aspect='unmarked'):

    form = construct_forms()[voice][aspect]
    return resolve(form, infinitive, person, number, voice, tense, aspect)


def resolve(form, infinitive, person, number, voice, tense, aspect):
    output = []
    for ff in form:
        if ff == ':verb':
            output.append(verb(infinitive, tense, person, number))
        elif ff == ':infinitive':
            output.append(infinitive)
        elif ff == ':present_participle':
            output.append(present_participle(infinitive))
        elif ff == ':past_participle':
            output.append(past_participle(infinitive))
        elif ff == ':have':
            output.append(verb('have', tense, person, number))
        elif ff == ':be':
            output.append(verb('be', tense, person, number))
        else:
            output.append(ff)

    return ' '.join(output)


def is_single_term_consonant(infinitive):
    for ww in irregulars.SINGLE_TERMINAL_CONSONANT:
        if infinitive.endswith(ww):
            return True
    return False


def present_participle(infinitive):
    if infinitive == 'be':
        return irregulars.BE['present_participle']
    if infinitive == 'have':
        return irregulars.HAVE['present_participle']
    cvc_regex = re.compile(r'.*' + CONSONANTS_PATTERN + VOWELS_PATTERN + CONSONANTS_PATTERN + '$')
    if cvc_regex.match(infinitive) and not is_single_term_consonant(infinitive):
        return present_participle_with_doubled_terminal_consonant_for(infinitive)
    if re.match(r'.*c$', infinitive):
        return infinitive + 'king'
    ing_matches = [r'.*ye$', r'.*oe$', r'.*nge$', r'.*ee$']
    for rr in ing_matches:
        if re.match(rr, infinitive):
            return infinitive + 'ing'
    if re.match(r'.*ie$', infinitive):
        return infinitive[0:-1] + 'ying'
    if re.match(r'.*e$', infinitive):
        return infinitive[0:-1] + 'ing'
    return infinitive + 'ing'


def preterite_for(infinitive):
    if infinitive in irregulars.IRREGULARS.keys():
        return irregulars.IRREGULARS[infinitive][0]
    cvc_regex = re.compile(r'.*' + CONSONANTS_PATTERN + VOWELS_PATTERN + CONSONANTS_PATTERN + '$')
    if cvc_regex.match(infinitive) and not is_single_term_consonant(infinitive):
        return regular_preterite_with_doubled_terminal_consonant_for(infinitive)
    d_matches = [r'.*' + CONSONANTS_PATTERN + 'e$', r'.*ye$', r'.*oe$', r'.*nge$', r'.*ee$']
    for rr in d_matches:
        if re.match(rr, infinitive):
            return infinitive + 'd'
    if re.match(r'.*' + CONSONANTS_PATTERN + 'y$', infinitive):
        return infinitive[0:-1] + 'ied'
    return infinitive + 'ed'


def regular_preterite_with_doubled_terminal_consonant_for(infinitive):
    preterite_for(infinitive + infinitive[-1])


def present_participle_with_doubled_terminal_consonant_for(infinitive):
    return present_participle(infinitive + infinitive[-1])


def present_third_person_singular_form_for(infinitive):
    if re.match(r'.*' + CONSONANTS_PATTERN + 'y$', infinitive):
        return infinitive[0:-1] + 'ies'
    es_matches = [r'.*' + CONSONANTS_PATTERN + 'o$', r'.*ss$', r'.*sh$', r'.*ch$', r'.*zz$', r'.*x$']
    for rr in es_matches:
        if re.match(rr, infinitive):
            return infinitive + 'es'
    if re.match(r'.*[^s]s$', infinitive):
        return infinitive + 'ses'
    return infinitive + 's'


def past_participle(infinitive):
    if infinitive == 'be':
        return irregulars.BE['past_participle']
    if infinitive == 'have':
        return irregulars.HAVE['past_participle']
    if infinitive in irregulars.IRREGULARS.keys():
        return irregulars.IRREGULARS[infinitive][1]
    return preterite_for(infinitive)


def verb(infinitive, tense, person, number):

    if tense == 'past' or tense == 'present':
        if infinitive == 'be':
            return irregulars.BE['finite'][tense][number][person]
        if infinitive == 'have':
            return irregulars.HAVE['finite'][tense][number][person]

    if tense == 'past':
        return preterite_for(infinitive)

    if tense == 'present':
        if person == 'third' and number == 'singular':
            return present_third_person_singular_form_for(infinitive)
        return infinitive

    if tense == 'future':
        return 'will ' + infinitive
