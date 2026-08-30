from flask import Flask, render_template_string, jsonify, request
import json
import os
import requests

app = Flask(__name__)

STATE_FILE = "state.json"


# ==========================================
# NOTIFICATIONS
# ==========================================

# Set to False when you're ready to send this to the real recipient.
# While True, no notifications are sent - safe for testing.
TESTING_MODE = True

# A webhook URL that receives a POST with a JSON body like {"content": "..."}.
# Easiest free option: https://ntfy.sh
#
# Example:
# NOTIFY_WEBHOOK_URL = "https://ntfy.sh/your-private-topic-name-here"
#
# Discord and Slack incoming webhook URLs also work.
NOTIFY_WEBHOOK_URL = ""


def send_notification(message):
    if TESTING_MODE or not NOTIFY_WEBHOOK_URL:
        return

    try:
        if "ntfy.sh" in NOTIFY_WEBHOOK_URL:
            requests.post(
                NOTIFY_WEBHOOK_URL,
                data=message.encode("utf-8"),
                timeout=5
            )
        else:
            requests.post(
                NOTIFY_WEBHOOK_URL,
                json={
                    "content": message,
                    "text": message
                },
                timeout=5
            )
    except Exception:
        # Never let a failed notification break the site.
        pass


# ==========================================
# CONFIGURATION
# ==========================================

SECURITY_QUESTION = "What is this guy's name?"

# Replace with your direct image URL, or leave as "" for text-only.
SECURITY_IMAGE_URL = "/static/lorentz.jpg"

ACCEPTED_ANSWERS = [
    "Lorentz",
    "lorentz"
]


# ==========================================
# INTRO MESSAGE
# ==========================================

INTRO_TITLE = "Hey Char"

INTRO_MESSAGE = """

I made a website. It took a while, but I knew I was going to wait until you had left Canada before sending it to you (which I think has happened). You were always great at making fun websites for me. I had to build a dedicated front- and back-end because there are a couple of tricks which I will explain in a minute. Simply put, I wanted to reach out, with some of my thoughts over the last couple of months. I knew what I wanted to say, but not how to say it, and ended up drafting a couple of versions. I realised that it was because I had no gauge as to how you were doing, and didn't want to upset you or come across in the wrong way, for why I couldn't get the message quite right. So, I built this website, and you can choose. Each message is similar in content, but with a bit of a different tone, and places emphasis on different things. You will choose one message to read, and the other two will be locked away. As far as I know, there is no way to unlock the other two messages once you choose, so be careful.

I thought about adding some fun easter eggs, but didn't want to overdo it. A nice colour scheme of sage green and sunset orange, along with the security question (well done on passing) should do it.

There is no pressure to reply, but feel free to reach out.

I really don't know how this will go down - it is quite daunting reaching out and being pretty vulnerable on here. All I know is that things ended so quickly, and I wanted to address a couple of things for good. Just to let you know, this website will automatically be taken down 24 hours after you choose to open one of the messages. If you wish to respond, take whatever time you need. Obviously you can copy/paste the messages, and do whatever you like, but it would be nice to keep this between us if possible.

"""


# ==========================================
# "I CAN'T CHOOSE" POPUP
# ==========================================

INDECISION_TITLE = "Not sure?"

INDECISION_MESSAGE = """
That's okay. Here's a bit more context to help:

There isn't really a "right" choice.

The three messages are similar in that they all come from the same place, but they focus on different things. One is more about how I feel now, one is more about what I have come to understand about what happened between us, and one is intended to give some closure.

You will only get to read one, so choose whichever feels most appropriate to you.

And if you genuinely don't want to read any of them, that's okay too.
"""


# ==========================================
# YOUR THREE MESSAGES
# ==========================================

MESSAGES = {

    # ======================================
    # MESSAGE 1 — HOW I FEEL
    # ======================================

    "1": """
Hey Char,

Firstly, I hope you are well. I really do. I hope you had an amazing time at home in Canada, as well as over your Summer break. It has been nice to watch along from a distance and see you enjoying yourself.

I don’t know how this message will find you. It may be a terrible idea to contact you, and perhaps one that I should never have opted for. I recognise that perhaps it is too soon, and you would rather time and space. I understand you may be hurt after everything that happened. Equally, perhaps you are happier now, moving forward with life, and finding peace in the distance between us. I really hope the time with your friends and family have left you with a positive mindset and some special memories.

I have tried my best - albeit with limited knowledge of your comings and goings - to time this message such that you will see it after you have left Canada. I do not want to interfere with the time you have with your family - something so special and important.

I understand I was reasonably firm about not wanting to be in contact. In hindsight, I think that this has been beneficial for me. I have needed time to process what happened, and remove myself from the immediacy of everything. I have come to terms with what has happened with a clearer head. I hope, with however you have approached the last couple of months, you also have gained some additional clarity.

I am not writing this message just to bug you, to interrupt your healing, or to elicit a response. I recognise you have no obligation to reply to me. I considered writing a physical letter, partly because I would not know when it had been received, and therefore it would place less immediate pressure on you to respond. In the end, I thought that the four or more weeks it may take for you to receive this, and potentially respond, may not be ideal in an ever-developing dynamic.

I have had a lot of time to think over the last weeks, and have isolated myself to have time to genuinely reflect, rather than seek the opinions of others. So much of what unfolded is so specific to just us, with the history and context that developed over time, that nobody aside from you would ever truly understand my words anyway. My thoughts below are not an attempt to reopen every argument we ever had, but they are instead the thoughts that have stayed with me, and the thoughts that I have come to understand differently, with some reflection. While I recognise it may be unorthodox to send such a lengthy message after months of no contact, I would forever regret not letting you know a couple of things.

I don’t really know how to start this, but I think the simplest thing I can say is that I miss you, and I miss what we had.

I miss you in the ways that I knew I would, but also so much more. I miss your voice, and your laugh. I miss calling you, and seeing notifications from you. I miss your touch, and your smell. I miss sleepovers, and the ordinary things that never feel significant until they are gone. I miss listening to music in your kitchen, eating too much Zambreros, and walking Russell together at sunset.

For so long, having you physically elsewhere was something I was learning to manage. It was difficult, and I hated the distance, but you were still my person.

Not having you here was hard, but not having you at all is near-impossible.

You knew me better than anyone, and I never had to explain myself around you. Eventually, I took this for granted, and now there is a strange absence where you used to be.

Life is okay. I am getting on with things. Being so very busy does help, but in the quiet times, at the end of the day, or on a Sunday afternoon, everything is quiet, and it’s your voice I wish I could hear the most.

I don’t want to make you feel guilty, or responsible for my happiness. You should just understand that losing you hasn’t been easy. You’ll feel as you read this, that this is a stripped back version of how we both used to feel, and it’s because while it is all true, it is difficult to be so vulnerable with someone I haven’t spoken to in so long. It is so tough carrying around years of memories and feelings regarding someone I no longer even speak to.

I’ve thought a lot about why things ended, and I’ve thought even more about my part in it. I want you to know that I am sorry. I am sorry I wasn’t more supportive of your goals, and your aspirations. I understand that these goals took you further away from me, but that was never why you did it. I was just bitter about the distance, and frustrated by what it meant for us, that I was not able to properly celebrate what it meant for you. You deserved to have somebody that was completely proud of you.

I understand I became complacent, and let frustration and resentment live where excitement and affection should have resided. I am also sorry that I didn’t tell you that you were loved enough. Part of me assumed you knew, part of me was frustrated, and saying it made the distance feel so much further. It’s not an excuse, I should have just told you, as you deserved to hear it.

I don’t know exactly how I feel now, but I find myself looking at charporkspriv more often than I’d care to admit, and listening to music that makes me think of you (I saw you saved my playlist). It’s so difficult moving on, and I would be lying if I said there wasn’t at least a part of me that has wanted to reach out just to hear from you for a while now.

That’s part of the reason why I’ve given you a choice in what you read. I could give you a tidy little goodbye, and move on, or I could break down why we went wrong, like I have in the other messages, but really, I know I miss you, at least a bit, so I might as well tell you.

I’m really proud of you. You are a truly special person, and I am glad you were brave and chased what you wanted to achieve. It is inspiring, and I hope you know that you have always inspired me, ever since we met as kids.

The point of this message is not to elicit a response from you, but to let you know that I miss you, and things aren’t easy. You don’t owe me anything: not an apology, not forgiveness, and not a response. Writing all three versions of these messages has helped me realise that I apologise for my role in our demise, verbalise how I feel, and move on regardless of how you feel in return.

I hope you are happy, and continue to be happy. Keep being brave each day and go out and get what you want, I am sure you are destined for great things, both personally and professionally. You have always been capable of so much, and I hope you get the best out of life.

P.S.

It was nice (and unexpected) to see your scientific photography entries. Also, I thought you would like these - sometimes I sit for a minute and think about sending you things, but up until now, I always resist.

https://www.instagram.com/reel/DcI-o-2ASa5/

https://www.instagram.com/reel/DcD8jwlkflb/

https://www.instagram.com/p/DZA_VRbCXVN/

There is plenty more I can say, and would like to share with you, but I will leave it there for now. This is just the bare-bones “if we were to never speak again, I would want her to know” explanation. If you have any thoughts, want me to elaborate, or just simply want to hear from me, let me know.
""",

    # ======================================
    # MESSAGE 2 — REFLECTION
    # ======================================

    "2": """
Hey Char,

Firstly, I hope you are well. I really do. I hope you had a lovely time travelling, and also with your family. I think it is special that you got to see them again.

I don’t know how this message will find you. It may be a terrible idea to contact you, and perhaps one that I should never have opted for. I recognise that perhaps it is too soon, and you would rather time and space. I understand you may be hurt after everything that happened. Equally, perhaps you are happier now, moving forward with life, and finding peace in the distance between us. I really hope the time with your friends and family have left you with a positive mindset and some special memories.

I have tried my best - albeit with limited knowledge of your comings and goings - to time this message such that you will see it after you have left Canada. I do not want to interfere with the time you have with your family - something so special and important.

I understand I was reasonably firm about not wanting to be in contact. In hindsight, I think that this has been beneficial for me. I have needed time to process what happened, and remove myself from the immediacy of everything. I have come to terms with what has happened with a clearer head. I hope, with however you have approached the last couple of months, you also have gained some additional clarity.

I am not writing this message just to bug you, to interrupt your healing, or to elicit a response. I recognise you have no obligation to reply to me. I considered writing a physical letter, partly because I would not know when it had been received, and therefore it would place less immediate pressure on you to respond. In the end, I thought that the four or more weeks it may take for you to receive this, and potentially respond, may not be ideal in an ever-developing dynamic.

I have had a lot of time to think over the last weeks, and have isolated myself to have time to genuinely reflect, rather than seek the opinions of others. So much of what unfolded is so specific to just us, with the history and context that developed over time, that nobody aside from you would ever truly understand my words anyway. My thoughts below are not an attempt to reopen every argument we ever had, but they are instead the thoughts that have stayed with me, and the thoughts that I have come to understand differently, with some reflection. While I recognise it may be unorthodox to send such a lengthy message after months of no contact, I would forever regret not letting you know a couple of things.

Resentment

We would often discuss resentment, and you feared I resented you. I thought this was unfair, as my anger and bitterness was, in my mind, directed at the distance, the time zones, and the duration of which we were apart. I thought I was frustrated with our circumstances, and not you.

However, as time progressed, and things got harder, I turned on you, and my resentment was not directed at the situation we found ourselves in; instead, it started to be directed at you. I was unfair in my assessment that you had put space between us, when in reality, you were simply taking advantage of the incredible opportunities presented to you. Of course, I knew this deep down, but it became increasingly difficult to realise this as time continued.

You were experiencing things that you had worked so hard for, and deserved. Not only did I grow to resent you for it, but I did not support you fully, as I should have. My interest in your life was minimal, my communication was poor, and I shut you out many times. For this, I am sorry.

Future Aspirations

I regret not speaking more earnestly with you about what I wanted us to become.

For a long time, I convinced myself that we shared no goals, ideas, or aspirations. This was something that we had spoken about previously, particularly towards the beginning of this year. I believed we were moving in opposite directions, and not building together. I have thought a lot about this since.

The truth is that I could never envision my life without you, but I never made it known to you. I believe the reason why I never thought we had a shared vision was accelerated by the fact that instead of asking you what you wanted your future to look like, I began to treat the absence of a clearly defined future as evidence that there couldn’t be one.

I regret we did not discuss what you wanted your life to look like, and I regret not speaking honestly about what I wanted. We could have seen if these things could have coexisted. Perhaps they could, perhaps they could not. I don’t know.

Past Issues

There is another thing I wish to mention, and it is the most important.

In the past, you have spoken very directly about the impact some of my behaviour had on your mental health, particularly throughout 2024-25. There is no excuse, and it has haunted me ever since. You were crying out for help, and I let you down. I look back now, and feel shame. Whatever difficulties I was dealing with myself, does not diminish the impact that my actions had on you.

If you were to only remember one thing from this message, I would want you to know that I am deeply sorry for the pain my actions caused. I do not expect an apology from you in return, and I am not trying to balance the scales between us. I want your last impression of me to be favourable, and I want you to know that I do not minimise the impact my actions had on you.

Distance

I believe, and always have believed, that ultimately, the distance and duration was what pushed us to breaking point. I do not want this to sound like deflection. We had problems, and both made mistakes - deliberate choices that put our relationship in jeopardy. I am not trying to erase that by attributing this to simply just circumstance.

However, I do believe the distance and duration was enormously significant. Each small issue, or misunderstanding, was amplified when our lives were so far removed from one another. Problems that could be resolved in an evening would stretch across days, and every small disagreement would end up a fight. We lost the ability to work together, against the problem, and instead, turned on each other at every opportunity.

I do not believe that distance created every problem we had, but I think it made our problems significantly harder to solve. Most importantly, I have realised that the last couple of years have been maintaining a relationship, instead of building one together.

You may not agree with my thoughts. You may see things differently, and I respect that. However, there is a part of me that feels that we were gradually forced apart by circumstance, rather than a point in which we stopped loving each other. Conversely, it could be that I am looking for an explanation that makes our ending easier to understand.

Future

This is likely the other reason I have spent so much time and energy reflecting on us.

In a few months, I will reach somewhat of a crossroads, in which, for the first time ever, I won’t be studying, and I have some decisions to make about what the next year(s) will look like. Until recently, I had been pretty set on taking a few months off, and maybe travelling around Australia or overseas before committing to anything long-term, whether it be employment or study.

But, really, I always thought it would be you that I would spend this time with. Pertaining to my previous point, I had a rough vision for us, which I never really got to share with you, as you have been away so often. It gradually became something that seemed increasingly unlikely, and I eventually stopped imagining it. But now, with everything that has happened, I find myself wondering what it could have been like.

I do not know what you plan to do once your internship ends. You have previously mentioned you may look to study, or even work, overseas. Maybe LEGO will want to keep you around. Perhaps you’ll come home and stay for a while. Maybe it’ll be something completely different, that both you and I couldn’t yet imagine. It is your life, and your decision, and I do not want this message to make you feel that you need to make any of those decisions with me in mind.

However, I want to be honest about something. If you do come home in a few months, and with enough time and distance from everything that has happened, you have developed your own thoughts and feelings, I don’t want to pretend that you couldn’t still be a part of this time.

I don’t want a decision from you, or a promise, or for you to come back. I just want you to know that the door is not closed, should the right circumstances arise.

Why I am sending this

Our final conversations happened so quickly, and I have realised that I had left some things on the table, and some thoughts unsaid. I don’t want to spend any more time regretting not being clear with you.

I do not know how you will react to what I have said. You may be angry, hurt, or upset. Perhaps you have completely moved on. These are all okay, and you do not owe me anything. These are just my honest thoughts, which you deserve to know.

I have written this at length because I wanted to give you everything at once, rather than send a vague message that leaves you wondering what I actually meant. If you choose not to respond, then at least you will have everything I wanted you to know. That is important to me, because whatever happens from here, I will be comfortable knowing that I have finally told you the things I have carried with me over the last few months.

Ultimately, this is simply my attempt to give you an honest and considered account of what I have come to understand over the last months, what I regret, and how I feel, so that nothing is left unsaid.

There is much more I could say, but I will leave it here. Your response to this message, which will be the contents of a message, or a lack of a reply, will give me direction on how to handle the following months.

I do not expect a response, and if you need time, take it.

If this is genuinely the last time we speak, then I want to wish you all the best for the rest of your LEGO internship, and for whatever comes afterwards.

You appear to be doing well, and I am genuinely glad to see that.

I am proud of you, and I miss you a lot <3

P.S.

It was nice (and unexpected) to see your scientific photography entries. Also, I thought you would like these - sometimes I sit for a minute and think about sending you things, but up until now, I always resist.

https://www.instagram.com/reel/DcI-o-2ASa5/

https://www.instagram.com/reel/DcD8jwlkflb/

https://www.instagram.com/p/DZA_VRbCXVN/

There is plenty more I can say, and would like to share with you, but I will leave it there for now. This is just the bare-bones “if we were to never speak again, I would want her to know” explanation. If you have any thoughts, want me to elaborate, or just simply want to hear from me, let me know.
""",

    # ======================================
    # MESSAGE 3 — CLOSURE
    # ======================================

    "3": """
Hey Char,

Firstly, I hope you are well. I really do. I hope you had an amazing time at home in Canada, as well as over your Summer break. It has been nice to watch along from a distance and see you enjoying yourself.

I don’t know how this message will find you. It may be a terrible idea to contact you, and perhaps one that I should never have opted for. I recognise that perhaps it is too soon, and you would rather time and space. I understand you may be hurt after everything that happened. Equally, perhaps you are happier now, moving forward with life, and finding peace in the distance between us. I really hope the time with your friends and family have left you with a positive mindset and some special memories.

I have tried my best - albeit with limited knowledge of your comings and goings - to time this message such that you will see it after you have left Canada. I do not want to interfere with the time you have with your family - something so special and important.

I understand I was reasonably firm about not wanting to be in contact. In hindsight, I think that this has been beneficial for me. I have needed time to process what happened, and remove myself from the immediacy of everything. I have come to terms with what has happened with a clearer head. I hope, with however you have approached the last couple of months, you also have gained some additional clarity.

I am not writing this message just to bug you, to interrupt your healing, or to elicit a response. I recognise you have no obligation to reply to me. I considered writing a physical letter, partly because I would not know when it had been received, and therefore it would place less immediate pressure on you to respond. In the end, I thought that the four or more weeks it may take for you to receive this, and potentially respond, may not be ideal in an ever-developing dynamic.

I have had a lot of time to think over the last weeks, and have isolated myself to have time to genuinely reflect, rather than seek the opinions of others. So much of what unfolded is so specific to just us, with the history and context that developed over time, that nobody aside from you would ever truly understand my words anyway. My thoughts below are not an attempt to reopen every argument we ever had, but they are instead the thoughts that have stayed with me, and the thoughts that I have come to understand differently, with some reflection. While I recognise it may be unorthodox to send such a lengthy message after months of no contact, I would forever regret not letting you know a couple of things.

I don’t really know how to start this, but I think the simplest thing I can say is that I miss you, and I miss what we had.

I miss you in the ways that I knew I would, but also so much more. I miss your voice, and your laugh. I miss calling you, and seeing notifications from you. I miss your touch, and your smell. I miss sleepovers, and the ordinary things that never feel significant until they are gone. I miss listening to music in your kitchen, eating too much Zambreros, and walking Russell together at sunset.

For so long, having you physically elsewhere was something I was learning to manage. It was difficult, and I hated the distance, but you were still my person.

Not having you here was hard, but not having you at all is near-impossible.

You knew me better than anyone, and I never had to explain myself around you. Eventually, I took this for granted, and now there is a strange absence where you used to be.

Life is okay. I am getting on with things. Being so very busy does help, but in the quiet times, at the end of the day, or on a Sunday afternoon, everything is quiet, and it's your voice I wish I could hear the most.

I don’t want to make you feel guilty, or responsible for my happiness. You should just understand that losing you hasn’t been easy. You’ll feel as you read this, that this is a stripped back version of how we both used to feel, and its because while it is all true, it is difficult to be so vulnerable with someone I haven’t spoken to in so long. It is so tough carrying around years of memories and feelings regarding someone I no longer even speak to.

I’ve thought a lot about why things ended, and I’ve thought even more about my part in it. I want you to know that I am sorry. I am sorry I wasn’t more supportive of your goals, and your aspirations. I understand that these goals took you further away from me, but that was never why you did it. I was just bitter about the distance, and frustrated by what it meant for us, that I was not able to properly celebrate what it meant for you. You deserved to have somebody that was completely proud of you.

I understand I became complacent, and let frustration and resentment live where excitement and affection should have resided. I am also sorry that I didn’t tell you that you were loved enough. Part of me assumed you knew, part of me was frustrated, and saying it made the distance feel so much further. It’s not an excuse, I should have just told you, as you deserved to hear it.

I don’t know exactly how I feel now, but I find myself looking at charporkspriv more often than I’d care to admit, and listening to music that makes me think of you (I saw you saved my playlist). It’s so difficult moving on, and I would be lying if I said there wasn’t at least a part of me that has wanted to reach out just to hear from you for a while now.

That’s part of the reason why I’ve given you a choice in what you read. I could give you a tidy little goodbye, and move on, or I could break down why we went wrong, like I have in the other messages, but really, I know I miss you, at least a bit, so I might as well tell you.

I’m really proud of you. You are a truly special person, and I am glad you were brave and chased what you wanted to achieve. It is inspiring, and I hope you know that you have always inspired me, ever since we met as kids.

The point of this message is not to elicit a response from you, but to let you know that I miss you, and things aren’t easy. You don’t owe me anything: not an apology, not forgiveness, and not a response. Writing all three versions of these messages has helped me realise that I apologise for my role in our demise, verbalise how I feel, and move forward, regardless of how you feel in return.

I hope you are happy, and continue to be happy. Keep being brave each day and go out and get what you want, I am sure you are destined for great things, both personally and professionally. You have always been capable of so much, and I hope you get the best out of life.

P.S.

It was nice (and unexpected) to see your scientific photography entries. Also, I thought you would like these - sometimes I sit for a minute and think about sending you things, but up until now, I always resist.

https://www.instagram.com/reel/DcI-o-2ASa5/

https://www.instagram.com/reel/DcD8jwlkflb/

https://www.instagram.com/p/DZA_VRbCXVN/

There is plenty more I can say, and would like to share with you, but I will leave it there for now. This is just the bare-bones “if we were to never speak again, I would want her to know” explanation. If you have any thoughts, want me to elaborate, or just simply want to hear from me, let me know.
"""
}


# ==========================================
# STATE MANAGEMENT
# ==========================================

def get_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass

    return {
        "chosen_option": None,
        "authenticated": False
    }


def save_state(state):
    temp_file = STATE_FILE + ".tmp"

    with open(temp_file, "w") as f:
        json.dump(state, f)
        f.flush()
        os.fsync(f.fileno())

    os.replace(temp_file, STATE_FILE)


# ==========================================
# HTML TEMPLATE
# ==========================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <title>Choose Wisely</title>

    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <style>

        :root {
            --bg-color: #f4f6f4;
            --card-bg: #ffffff;
            --text-main: #2c3531;
            --text-muted: #65746b;
            --accent-color: #e07a5f;
            --accent-hover: #cc6b50;
            --accent-active: #81b29a;
            --locked-bg: #e2e8e4;
            --locked-text: #94a39b;
            --border-radius: 16px;
        }


        body {

            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Roboto,
                sans-serif;

            color: var(--text-main);

            text-align: center;

            padding: 20px;

            margin: 0;

            display: flex;

            justify-content: center;

            align-items: center;

            min-height: 100vh;

            box-sizing: border-box;

            background-color: var(--bg-color);

            position: relative;

            overflow: hidden;
        }


        #particle-canvas {

            position: fixed;

            top: 0;

            left: 0;

            width: 100%;

            height: 100%;

            display: block;

            z-index: 0;
        }


        .card {

            position: relative;

            z-index: 1;

            background-color: var(--card-bg);

            padding: 35px 30px;

            border-radius: var(--border-radius);

            max-width: 440px;

            width: 100%;

            box-shadow:
                0 10px 30px rgba(44, 53, 49, 0.06);

            border:
                1px solid rgba(129, 178, 154, 0.2);

            box-sizing: border-box;
        }


        h2 {

            margin-top: 0;

            font-size: 1.6rem;

            letter-spacing: -0.02em;

            color: var(--text-main);
        }


        p {

            color: var(--text-muted);

            font-size: 0.95rem;

            line-height: 1.6;
        }


        .question-image {

            width: 100%;

            max-height: 200px;

            object-fit: cover;

            border-radius:
                calc(var(--border-radius) - 8px);

            margin-bottom: 15px;

            border:
                1px solid rgba(129, 178, 154, 0.2);
        }


        .input-group,
        .button-group {

            margin-top: 20px;

            display: flex;

            flex-direction: column;

            gap: 12px;
        }


        input[type="text"] {

            width: 100%;

            padding: 12px 14px;

            font-size: 1rem;

            border: 1px solid #cbd5e1;

            border-radius:
                calc(var(--border-radius) - 6px);

            box-sizing: border-box;

            background-color: #f8fafc;

            color: var(--text-main);

            outline: none;

            transition: border-color 0.2s;
        }


        input[type="text"]:focus {

            border-color: var(--accent-color);
        }


        button {

            display: block;

            width: 100%;

            padding: 14px;

            font-size: 1rem;

            font-weight: 600;

            border: none;

            border-radius:
                calc(var(--border-radius) - 6px);

            cursor: pointer;

            background-color: var(--accent-color);

            color: #ffffff;

            transition:
                background-color 0.2s,
                transform 0.1s;
        }


        button:hover:not(:disabled) {

            background-color: var(--accent-hover);
        }


        button:active:not(:disabled) {

            transform: scale(0.98);
        }


        button:disabled {

            background-color: var(--locked-bg);

            color: var(--locked-text);

            cursor: not-allowed;
        }


        .envelope-btn {

            display: flex;

            align-items: center;

            justify-content: center;

            gap: 10px;

            width: 100%;

            padding: 14px;

            font-size: 1rem;

            font-weight: 600;

            border: none;

            border-radius:
                calc(var(--border-radius) - 6px);

            cursor: pointer;

            background-color: var(--accent-color);

            color: #ffffff;

            transition:
                background-color 0.2s,
                transform 0.1s;
        }


        .envelope-btn:hover:not(:disabled) {

            background-color: var(--accent-hover);
        }


        .envelope-btn:active:not(:disabled) {

            transform: scale(0.98);
        }


        .envelope-btn:disabled {

            background-color: var(--locked-bg);

            color: var(--locked-text);

            cursor: not-allowed;
        }


        .envelope-btn svg {

            flex-shrink: 0;
        }


        button.secondary {

            background-color: transparent;

            color: var(--text-muted);

            border: 1px solid #cbd5e1;
        }


        button.secondary:hover:not(:disabled) {

            background-color: #f1f5f2;
        }


        #result {

            margin-top: 25px;

            padding: 20px;

            background-color: #f7f9f7;

            border-left:
                4px solid var(--accent-active);

            border-radius: 8px;

            text-align: left;

            word-break: break-word;

            border:
                1px solid rgba(129, 178, 154, 0.15);

            border-left-width: 4px;
        }


        #result p {

            color: var(--text-main);

            line-height: 1.7;

            white-space: pre-wrap;

            margin-top: 8px;

            margin-bottom: 0;
        }


        .hidden {

            display: none !important;
        }


        /* =====================================
           MODALS
        ====================================== */

        .modal-overlay {

            position: fixed;

            top: 0;

            left: 0;

            width: 100%;

            height: 100%;

            background:
                rgba(44, 53, 49, 0.55);

            display: flex;

            justify-content: center;

            align-items: center;

            z-index: 1000;

            padding: 20px;

            box-sizing: border-box;
        }


        .modal-box {

            background-color: var(--card-bg);

            border-radius: var(--border-radius);

            max-width: 440px;

            width: 100%;

            max-height: 80vh;

            display: flex;

            flex-direction: column;

            box-shadow:
                0 10px 30px rgba(44, 53, 49, 0.2);

            border:
                1px solid rgba(129, 178, 154, 0.2);

            overflow: hidden;
        }


        .modal-header {

            padding: 25px 25px 10px 25px;
        }


        .modal-header h2 {

            margin: 0;
        }


        .modal-body {

            padding: 10px 25px;

            overflow-y: auto;

            text-align: left;

            color: var(--text-main);

            font-size: 0.95rem;

            line-height: 1.7;

            white-space: pre-wrap;
        }


        .modal-footer {

            padding:
                15px 25px 25px 25px;

            display: flex;

            flex-direction: column;

            gap: 10px;
        }

    </style>

</head>


<body>

    <canvas id="particle-canvas"></canvas>


    <!-- ======================================
         MAIN CARD
    ======================================= -->

    <div class="card">

        <h2>Choose Wisely</h2>


        <!-- SECURITY QUESTION -->

        <div id="auth-section">

            {% if image_url %}

            <img
                src="{{ image_url }}"
                alt="Security Question Hint"
                class="question-image"
            >

            {% endif %}


            <p id="question-label">
                {{ question }}
            </p>


            <div class="input-group">

                <input
                    type="text"
                    id="answer-input"
                    placeholder="Enter your answer..."
                    onkeypress="handleKeyPress(event)"
                >


                <button
                    onclick="playClick(); verifyAnswer()"
                >
                    Verify Answer
                </button>

            </div>


            <p
                id="error-msg"
                style="
                    color: var(--accent-color);
                    font-size: 0.85rem;
                    margin-top: 10px;
                "
                class="hidden"
            >
                Incorrect answer. Try again.
            </p>

        </div>


        <!-- MESSAGE CHOICE -->

        <div id="choice-section" class="hidden">

            <p id="status">
                Verified! Once you select a message, the server will permanently lock the other two.
            </p>


            <div class="button-group">


                <!-- MESSAGE 1 -->

                <button
                    id="btn1"
                    class="envelope-btn"
                    onclick="playClick(); requestChoice('1')"
                >

                    <svg
                        id="env-icon-1"
                        width="28"
                        height="20"
                        viewBox="0 0 28 20"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                    >

                        <rect
                            x="1"
                            y="1"
                            width="26"
                            height="18"
                            rx="2"
                            stroke="white"
                            stroke-width="1.5"
                        />

                        <path
                            d="M2 2L14 12L26 2"
                            stroke="white"
                            stroke-width="1.5"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        />

                        <circle
                            cx="20"
                            cy="6"
                            r="2.5"
                            fill="white"
                        />

                    </svg>

                    <span>Message 1</span>

                </button>


                <!-- MESSAGE 2 -->

                <button
                    id="btn2"
                    class="envelope-btn"
                    onclick="playClick(); requestChoice('2')"
                >

                    <svg
                        id="env-icon-2"
                        width="28"
                        height="20"
                        viewBox="0 0 28 20"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                    >

                        <rect
                            x="1"
                            y="1"
                            width="26"
                            height="18"
                            rx="2"
                            stroke="white"
                            stroke-width="1.5"
                        />

                        <path
                            d="M2 2L14 12L26 2"
                            stroke="white"
                            stroke-width="1.5"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        />

                        <circle
                            cx="20"
                            cy="6"
                            r="2.5"
                            fill="white"
                        />

                    </svg>

                    <span>Message 2</span>

                </button>


                <!-- MESSAGE 3 -->

                <button
                    id="btn3"
                    class="envelope-btn"
                    onclick="playClick(); requestChoice('3')"
                >

                    <svg
                        id="env-icon-3"
                        width="28"
                        height="20"
                        viewBox="0 0 28 20"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                    >

                        <rect
                            x="1"
                            y="1"
                            width="26"
                            height="18"
                            rx="2"
                            stroke="white"
                            stroke-width="1.5"
                        />

                        <path
                            d="M2 2L14 12L26 2"
                            stroke="white"
                            stroke-width="1.5"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        />

                        <circle
                            cx="20"
                            cy="6"
                            r="2.5"
                            fill="white"
                        />

                    </svg>

                    <span>Message 3</span>

                </button>

            </div>


            <!-- INDECISION -->

            <button
                id="indecision-btn"
                class="secondary"
                style="margin-top: 12px;"
                onclick="playClick(); showIndecision()"
            >
                I can't choose
            </button>


            <!-- RESULT -->

            <div
                id="result"
                class="hidden"
            ></div>

        </div>

    </div>


    <!-- ======================================
         INTRO MODAL
    ======================================= -->

    <div
        id="intro-modal"
        class="modal-overlay hidden"
    >

        <div class="modal-box">

            <div class="modal-header">

                <h2>
                    {{ intro_title }}
                </h2>

            </div>


            <div
                class="modal-body"
                id="intro-body"
            ></div>


            <div class="modal-footer">

                <button
                    id="intro-continue-btn"
                    onclick="playClick(); closeIntro()"
                    disabled
                >
                    I've read this
                </button>

            </div>

        </div>

    </div>


    <!-- ======================================
         CONFIRMATION MODAL
    ======================================= -->

    <div
        id="confirm-modal"
        class="modal-overlay hidden"
    >

        <div class="modal-box">

            <div class="modal-header">

                <h2>
                    Are you sure?
                </h2>

            </div>


            <div class="modal-body">

                <p style="margin:0;">

                    Once you choose, the other two messages lock forever.
                    There's no way back from here.

                </p>

            </div>


            <div class="modal-footer">

                <button
                    id="confirm-yes-btn"
                    onclick="playClick(); confirmChoice()"
                    disabled
                >
                    Yes, I'm sure
                </button>


                <button
                    class="secondary"
                    onclick="playClick(); cancelChoice()"
                >
                    Wait, not yet
                </button>

            </div>

        </div>

    </div>


    <!-- ======================================
         INDECISION MODAL
    ======================================= -->

    <div
        id="indecision-modal"
        class="modal-overlay hidden"
    >

        <div class="modal-box">

            <div class="modal-header">

                <h2>
                    {{ indecision_title }}
                </h2>

            </div>


            <div
                class="modal-body"
                style="white-space: pre-wrap;"
            >
                {{ indecision_message }}
            </div>


            <div class="modal-footer">

                <button
                    onclick="playClick(); closeIndecision()"
                >
                    Okay
                </button>

            </div>

        </div>

    </div>


    <script>

        // ==========================================
        // INTERACTIVE PARTICLE FIELD
        // ==========================================

        (function() {

            const canvas =
                document.getElementById('particle-canvas');

            if (!canvas) {
                console.error(
                    'particle-canvas element not found'
                );
                return;
            }


            const ctx =
                canvas.getContext('2d');

            if (!ctx) {
                console.error(
                    '2D canvas context not available'
                );
                return;
            }


            let width;
            let height;
            let particles;


            const colors = [
                '#81b29a',
                '#e07a5f',
                '#a8c4b4',
                '#eba488'
            ];


            const mouse = {
                x: -9999,
                y: -9999,
                active: false
            };


            function resize() {

                width =
                    canvas.width =
                    window.innerWidth;

                height =
                    canvas.height =
                    window.innerHeight;

            }


            function initParticles() {

                const count =
                    Math.min(
                        140,
                        Math.floor(
                            (width * height) / 9000
                        )
                    );


                particles = [];


                for (
                    let i = 0;
                    i < count;
                    i++
                ) {

                    particles.push({

                        x:
                            Math.random() *
                            width,

                        y:
                            Math.random() *
                            height,

                        vx:
                            (Math.random() - 0.5)
                            * 0.4,

                        vy:
                            (Math.random() - 0.5)
                            * 0.4,

                        r:
                            Math.random()
                            * 2.5 + 2,

                        color:
                            colors[
                                Math.floor(
                                    Math.random()
                                    * colors.length
                                )
                            ]

                    });

                }

            }


            function step() {

                ctx.clearRect(
                    0,
                    0,
                    width,
                    height
                );


                for (let p of particles) {

                    p.x += p.vx;
                    p.y += p.vy;


                    // Wrap around edges

                    if (p.x < -10)
                        p.x = width + 10;

                    if (p.x > width + 10)
                        p.x = -10;

                    if (p.y < -10)
                        p.y = height + 10;

                    if (p.y > height + 10)
                        p.y = -10;


                    // Mouse interaction

                    if (mouse.active) {

                        const dx =
                            p.x - mouse.x;

                        const dy =
                            p.y - mouse.y;

                        const dist =
                            Math.sqrt(
                                dx * dx +
                                dy * dy
                            );

                        const radius = 130;


                        if (
                            dist < radius &&
                            dist > 0.01
                        ) {

                            const force =
                                (1 - dist / radius)
                                * 1.8;


                            p.x +=
                                (dx / dist)
                                * force;

                            p.y +=
                                (dy / dist)
                                * force;

                        }

                    }


                    // Particle

                    ctx.beginPath();

                    ctx.arc(
                        p.x,
                        p.y,
                        p.r,
                        0,
                        Math.PI * 2
                    );

                    ctx.fillStyle =
                        p.color;

                    ctx.globalAlpha = 0.8;

                    ctx.fill();

                }


                // Connecting lines

                ctx.globalAlpha = 1;


                for (
                    let i = 0;
                    i < particles.length;
                    i++
                ) {

                    for (
                        let j = i + 1;
                        j < particles.length;
                        j++
                    ) {

                        const a =
                            particles[i];

                        const b =
                            particles[j];


                        const dx =
                            a.x - b.x;

                        const dy =
                            a.y - b.y;

                        const dist =
                            Math.sqrt(
                                dx * dx +
                                dy * dy
                            );


                        if (dist < 130) {

                            ctx.beginPath();

                            ctx.moveTo(
                                a.x,
                                a.y
                            );

                            ctx.lineTo(
                                b.x,
                                b.y
                            );


                            ctx.strokeStyle =
                                'rgba(129, 178, 154, ' +
                                (
                                    0.35 *
                                    (1 - dist / 130)
                                ) +
                                ')';


                            ctx.lineWidth = 1.2;

                            ctx.stroke();

                        }

                    }

                }


                requestAnimationFrame(step);

            }


            window.addEventListener(
                'resize',
                () => {
                    resize();
                    initParticles();
                }
            );


            window.addEventListener(
                'mousemove',
                (e) => {

                    mouse.x =
                        e.clientX;

                    mouse.y =
                        e.clientY;

                    mouse.active = true;

                }
            );


            window.addEventListener(
                'mouseleave',
                () => {
                    mouse.active = false;
                }
            );


            window.addEventListener(
                'touchmove',
                (e) => {

                    if (
                        e.touches.length > 0
                    ) {

                        mouse.x =
                            e.touches[0].clientX;

                        mouse.y =
                            e.touches[0].clientY;

                        mouse.active = true;

                    }

                },
                {
                    passive: true
                }
            );


            window.addEventListener(
                'touchend',
                () => {
                    mouse.active = false;
                }
            );


            resize();

            initParticles();

            step();

        })();


        // ==========================================
        // GLOBAL STATE
        // ==========================================

        let introShown = false;
        let pendingChoice = null;
        let countdownTimer = null;


        // ==========================================
        // SOUND EFFECT
        // ==========================================

        let audioCtx = null;


        function playClick() {

            try {

                if (!audioCtx) {

                    audioCtx =
                        new (
                            window.AudioContext ||
                            window.webkitAudioContext
                        )();

                }


                const osc =
                    audioCtx.createOscillator();

                const gain =
                    audioCtx.createGain();


                osc.type = 'sine';


                osc.frequency.setValueAtTime(
                    520,
                    audioCtx.currentTime
                );


                osc.frequency.exponentialRampToValueAtTime(
                    280,
                    audioCtx.currentTime + 0.09
                );


                gain.gain.setValueAtTime(
                    0.12,
                    audioCtx.currentTime
                );


                gain.gain.exponentialRampToValueAtTime(
                    0.001,
                    audioCtx.currentTime + 0.12
                );


                osc
                    .connect(gain)
                    .connect(
                        audioCtx.destination
                    );


                osc.start();

                osc.stop(
                    audioCtx.currentTime + 0.12
                );

            } catch (e) {
                // Audio unavailable:
                // fail silently.
            }

        }


        // ==========================================
        // INTRO
        // ==========================================

        function typewriteIntro() {

            const el =
                document.getElementById(
                    'intro-body'
                );


            const btn =
                document.getElementById(
                    'intro-continue-btn'
                );


            el.textContent =
                {{ intro_message|tojson }};


            btn.disabled = false;

        }


        function showIntroOrChoice() {

            if (!introShown) {

                document
                    .getElementById('intro-modal')
                    .classList
                    .remove('hidden');


                typewriteIntro();

            } else {

                document
                    .getElementById('choice-section')
                    .classList
                    .remove('hidden');

            }

        }


        function closeIntro() {

            introShown = true;


            document
                .getElementById('intro-modal')
                .classList
                .add('hidden');


            document
                .getElementById('choice-section')
                .classList
                .remove('hidden');

        }


        // ==========================================
        // INDECISION
        // ==========================================

        function showIndecision() {

            document
                .getElementById('indecision-modal')
                .classList
                .remove('hidden');

        }


        function closeIndecision() {

            document
                .getElementById('indecision-modal')
                .classList
                .add('hidden');

        }


        // ==========================================
        // AUTHENTICATION
        // ==========================================

        async function verifyAnswer() {

            const input =
                document.getElementById(
                    'answer-input'
                );


            const answer =
                input.value;


            try {

                const res =
                    await fetch(
                        '/verify',
                        {
                            method: 'POST',

                            headers: {
                                'Content-Type':
                                    'application/json'
                            },

                            body:
                                JSON.stringify({
                                    answer: answer
                                })
                        }
                    );


                const data =
                    await res.json();


                if (data.success) {

                    document
                        .getElementById('auth-section')
                        .classList
                        .add('hidden');


                    showIntroOrChoice();

                } else {

                    const err =
                        document.getElementById(
                            'error-msg'
                        );


                    err
                        .classList
                        .remove('hidden');


                    input.value = "";

                    input.focus();

                }

            } catch (e) {

                console.error(e);

                alert(
                    "Something went wrong. Please try again."
                );

            }

        }


        function handleKeyPress(e) {

            if (e.key === 'Enter') {

                verifyAnswer();

            }

        }


        // ==========================================
        // CHOICE REQUEST
        // ==========================================

        function requestChoice(option) {

            // Don't allow another choice while
            // the confirmation countdown is active.
            if (pendingChoice !== null) {
                return;
            }


            pendingChoice = option;


            const yesBtn =
                document.getElementById(
                    'confirm-yes-btn'
                );


            yesBtn.disabled = true;


            document
                .getElementById('confirm-modal')
                .classList
                .remove('hidden');


            // Clear any previous countdown.

            if (countdownTimer !== null) {

                clearInterval(
                    countdownTimer
                );

                countdownTimer = null;

            }


            // Five-second countdown.

            let secondsLeft = 5;


            yesBtn.innerText =
                `Yes, I'm sure (${secondsLeft})`;


            countdownTimer =
                setInterval(
                    () => {

                        secondsLeft -= 1;


                        if (secondsLeft > 0) {

                            yesBtn.innerText =
                                `Yes, I'm sure (${secondsLeft})`;

                        } else {

                            clearInterval(
                                countdownTimer
                            );

                            countdownTimer = null;


                            yesBtn.innerText =
                                "Yes, I'm sure";


                            yesBtn.disabled =
                                false;

                        }

                    },
                    1000
                );

        }


        function cancelChoice() {

            pendingChoice = null;


            if (countdownTimer !== null) {

                clearInterval(
                    countdownTimer
                );

                countdownTimer = null;

            }


            const yesBtn =
                document.getElementById(
                    'confirm-yes-btn'
                );


            yesBtn.innerText =
                "Yes, I'm sure";


            yesBtn.disabled = true;


            document
                .getElementById(
                    'confirm-modal'
                )
                .classList
                .add('hidden');

        }


        // ==========================================
        // CONFIRM CHOICE
        // ==========================================

        async function confirmChoice() {

            if (!pendingChoice) {
                return;
            }


            const option =
                pendingChoice;


            if (countdownTimer !== null) {

                clearInterval(
                    countdownTimer
                );

                countdownTimer = null;

            }


            document
                .getElementById('confirm-modal')
                .classList
                .add('hidden');


            try {

                const res =
                    await fetch(
                        '/choose',
                        {
                            method: 'POST',

                            headers: {
                                'Content-Type':
                                    'application/json'
                            },

                            body:
                                JSON.stringify({
                                    choice: option
                                })
                        }
                    );


                const data =
                    await res.json();


                if (data.success) {

                    applyLock(
                        option,
                        data.message
                    );

                } else {

                    alert(data.error);

                    checkState();

                }

            } catch (e) {

                console.error(e);

                alert(
                    "Network error. Please try again."
                );

                checkState();

            }


            pendingChoice = null;

        }


        // ==========================================
        // APPLY PERMANENT LOCK
        // ==========================================

        function applyLock(chosen, msg) {

            // Hide "I can't choose"

            document
                .getElementById(
                    'indecision-btn'
                )
                .classList
                .add('hidden');


            // Lock all envelopes

            document
                .querySelectorAll(
                    '#choice-section .envelope-btn'
                )
                .forEach(
                    (b, index) => {

                        b.disabled = true;


                        const num =
                            index + 1;


                        const label =
                            b.querySelector(
                                'span'
                            );


                        const icon =
                            b.querySelector(
                                'svg'
                            );


                        // ==================================
                        // CHOSEN MESSAGE
                        // ==================================

                        if (
                            num.toString() === chosen
                        ) {

                            b.style.backgroundColor =
                                "var(--accent-active)";


                            label.textContent =
                                `Message ${chosen} (Opened)`;


                            // Open envelope

                            icon.innerHTML = `

                                <path
                                    d="M2 6L14 14L26 6"
                                    stroke="white"
                                    stroke-width="1.5"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    fill="none"
                                />

                                <rect
                                    x="6"
                                    y="1"
                                    width="16"
                                    height="12"
                                    rx="1"
                                    stroke="white"
                                    stroke-width="1.5"
                                    fill="none"
                                />

                                <rect
                                    x="1"
                                    y="6"
                                    width="26"
                                    height="13"
                                    rx="2"
                                    stroke="white"
                                    stroke-width="1.5"
                                    fill="none"
                                />

                            `;


                        // ==================================
                        // LOCKED MESSAGES
                        // ==================================

                        } else {

                            label.textContent =
                                `Message ${num} (Locked)`;


                            icon.innerHTML = `

                                <rect
                                    x="1"
                                    y="1"
                                    width="26"
                                    height="18"
                                    rx="2"
                                    stroke="currentColor"
                                    stroke-width="1.5"
                                    fill="none"
                                />

                                <path
                                    d="M2 2L14 12L26 2"
                                    stroke="currentColor"
                                    stroke-width="1.5"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    fill="none"
                                />

                                <circle
                                    cx="20"
                                    cy="6"
                                    r="2.5"
                                    fill="currentColor"
                                />

                            `;

                        }

                    }
                );


            // Update status

            document
                .getElementById('status')
                .innerText =
                "Choice permanently registered on server. Other options are locked.";


            // ==========================================
            // DISPLAY MESSAGE
            // ==========================================

            const resBox =
                document.getElementById(
                    'result'
                );


            resBox.classList.remove(
                'hidden'
            );


            // Clear existing content

            resBox.innerHTML = "";


            // Message heading

            const heading =
                document.createElement(
                    'strong'
                );


            heading.style.color =
                "var(--accent-color)";


            heading.textContent =
                "Message " + chosen + ":";


            // Message body

            const message =
                document.createElement(
                    'p'
                );


            message.style.marginTop =
                "8px";


            message.style.color =
                "var(--text-main)";


            message.style.whiteSpace =
                "pre-wrap";


            message.textContent =
                msg;


            // Put them into result box

            resBox.appendChild(
                heading
            );

            resBox.appendChild(
                message
            );

        }


        // ==========================================
        // CHECK SERVER STATE
        // ==========================================

        async function checkState() {

            try {

                const res =
                    await fetch(
                        '/status?' +
                        new Date().getTime()
                    );


                const data =
                    await res.json();


                // A choice has already been made.

                if (data.chosen_option) {

                    document
                        .getElementById(
                            'auth-section'
                        )
                        .classList
                        .add('hidden');


                    document
                        .getElementById(
                            'intro-modal'
                        )
                        .classList
                        .add('hidden');


                    document
                        .getElementById(
                            'confirm-modal'
                        )
                        .classList
                        .add('hidden');


                    document
                        .getElementById(
                            'indecision-modal'
                        )
                        .classList
                        .add('hidden');


                    document
                        .getElementById(
                            'choice-section'
                        )
                        .classList
                        .remove('hidden');


                    applyLock(
                        data.chosen_option,
                        data.message
                    );


                // Authenticated but hasn't chosen.

                } else if (
                    data.authenticated
                ) {

                    document
                        .getElementById(
                            'auth-section'
                        )
                        .classList
                        .add('hidden');


                    showIntroOrChoice();

                }

            } catch (e) {

                console.error(e);

            }

        }


        // Initial state check.

        checkState();


        // Continue checking state every 3 seconds.

        setInterval(
            checkState,
            3000
        );

    </script>

</body>

</html>
"""


# ==========================================
# ROUTES
# ==========================================

@app.route('/')
def home():

    send_notification(
        "🔗 The link has been accessed."
    )

    return render_template_string(
        HTML_TEMPLATE,
        question=SECURITY_QUESTION,
        image_url=SECURITY_IMAGE_URL,
        intro_title=INTRO_TITLE,
        intro_message=INTRO_MESSAGE,
        indecision_title=INDECISION_TITLE,
        indecision_message=INDECISION_MESSAGE
    )


@app.route('/status', methods=['GET'])
def status():

    state = get_state()

    chosen = state.get(
        "chosen_option"
    )

    authenticated = state.get(
        "authenticated",
        False
    )

    if chosen:

        return jsonify({
            "chosen_option": chosen,
            "message": MESSAGES[chosen],
            "authenticated": True
        })

    return jsonify({
        "chosen_option": None,
        "authenticated": authenticated
    })


@app.route('/verify', methods=['POST'])
def verify():

    req_data = request.get_json(
        silent=True
    ) or {}

    user_answer = req_data.get(
        "answer",
        ""
    )

    if not isinstance(user_answer, str):
        user_answer = str(user_answer)

    user_answer = user_answer.strip().lower()

    if user_answer in [
        answer.lower()
        for answer in ACCEPTED_ANSWERS
    ]:

        state = get_state()

        state["authenticated"] = True

        save_state(state)

        return jsonify({
            "success": True
        })

    return jsonify({
        "success": False
    }), 400


@app.route('/choose', methods=['POST'])
def choose():

    state = get_state()

    # Must authenticate first.

    if not state.get(
        "authenticated",
        False
    ):

        return jsonify({
            "success": False,
            "error": "Not authenticated!"
        }), 403


    # Choice already made.

    if state.get(
        "chosen_option"
    ) is not None:

        return jsonify({
            "success": False,
            "error":
                "A choice has already been made and locked!"
        }), 400


    req_data = request.get_json(
        silent=True
    ) or {}


    choice = str(
        req_data.get(
            "choice",
            ""
        )
    )


    # Valid choice.

    if choice in MESSAGES:

        state["chosen_option"] = choice

        save_state(state)

        send_notification(
            f"💌 A choice has been made: Message {choice} was opened."
        )

        return jsonify({
            "success": True,
            "message": MESSAGES[choice]
        })


    return jsonify({
        "success": False,
        "error": "Invalid choice"
    }), 400


@app.route('/reset')
def reset_state():

    if os.path.exists(
        STATE_FILE
    ):

        os.remove(
            STATE_FILE
        )

    return "State has been reset!"


# ==========================================
# RUN APP
# ==========================================

if __name__ == '__main__':

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
