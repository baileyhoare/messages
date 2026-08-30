from flask import Flask, render_template_string, jsonify, request
import json
import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__)

STATE_FILE = "state.json"

# ============================================================
# NOTIFICATIONS
# ============================================================

# IMPORTANT:
# Set this to False when you are ready for the real test.
TESTING_MODE = False

# Put your ntfy.sh URL here.
#
# Example:
# NOTIFY_WEBHOOK_URL = "https://ntfy.sh/your-private-topic"
#
# You can also use another webhook service.
NOTIFY_WEBHOOK_URL = "https://ntfy.sh/bailey-char-messages-030621"


def now_adelaide():
    """
    Return the current time in Adelaide.
    """
    return datetime.now(
        ZoneInfo("Australia/Adelaide")
    )


def formatted_time(dt=None):
    """
    Return a human-readable Adelaide timestamp.
    """
    if dt is None:
        dt = now_adelaide()

    return dt.strftime(
        "%A, %d %B %Y at %I:%M:%S %p"
    )


def iso_time(dt=None):
    """
    Return a timestamp suitable for storing in state.json.
    """
    if dt is None:
        dt = now_adelaide()

    return dt.isoformat()


def parse_time(value):
    """
    Convert a stored ISO timestamp back into a datetime.
    """
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def format_elapsed(seconds):
    """
    Convert seconds into a readable duration.
    """

    if seconds < 0:
        seconds = 0

    seconds = int(seconds)

    days = seconds // 86400
    seconds %= 86400

    hours = seconds // 3600
    seconds %= 3600

    minutes = seconds // 60
    seconds %= 60

    parts = []

    if days:
        parts.append(
            f"{days} day{'s' if days != 1 else ''}"
        )

    if hours:
        parts.append(
            f"{hours} hour{'s' if hours != 1 else ''}"
        )

    if minutes:
        parts.append(
            f"{minutes} minute{'s' if minutes != 1 else ''}"
        )

    if seconds or not parts:
        parts.append(
            f"{seconds} second{'s' if seconds != 1 else ''}"
        )

    return ", ".join(parts)


def send_notification(message):
    """
    Send a notification.

    If TESTING_MODE is True, nothing is sent.
    """

    if TESTING_MODE:
        print(
            "[TESTING MODE] Notification:"
        )
        print(message)
        return

    if not NOTIFY_WEBHOOK_URL:
        print(
            "[WARNING] NOTIFY_WEBHOOK_URL is empty."
        )
        print(message)
        return

    try:

        if "ntfy.sh" in NOTIFY_WEBHOOK_URL:

            response = requests.post(
                NOTIFY_WEBHOOK_URL,
                data=message.encode("utf-8"),
                headers={
                    "Title": "Char Messages"
                },
                timeout=5
            )

        else:

            response = requests.post(
                NOTIFY_WEBHOOK_URL,
                json={
                    "content": message,
                    "text": message
                },
                timeout=5
            )

        print(
            "Notification sent:",
            response.status_code
        )

    except Exception as e:

        print(
            "[WARNING] Notification failed:",
            e
        )


# ============================================================
# CONFIGURATION
# ============================================================

SECURITY_QUESTION = "What is this guy's name?"

SECURITY_IMAGE_URL = "/static/lorentz.jpg"

ACCEPTED_ANSWERS = [
    "Lorentz",
    "lorentz"
]


# ============================================================
# INTRO MESSAGE
# ============================================================

INTRO_TITLE = "Hey Char"

INTRO_MESSAGE = """

I made a website. It took a while, but I knew I was going to wait until you had left Canada before sending it to you (which I think has happened). You were always great at making fun websites for me. I had to build a dedicated front- and back-end because there are a couple of tricks which I will explain shortly.

Simply put, I wanted to reach out, with some of my thoughts over the last couple of months. I knew what I wanted to say, but not how to say it, and ended up drafting a couple of versions. I realised that it was because I had no gauge as to how you were doing, and didn't want to upset you or come across in the wrong way, for why I couldn't get the message quite right.

So, I built this website, and you can choose. I understand choosing is difficult, especially for you. Do not worry too much, the messages all say more or less the same thing, but each one has a different purpose and emphasis.

Message 1 is the most personal. It is mainly about how I feel now: missing you, what I remember about us, what I regret, and the things I have found difficult since we stopped speaking. It is probably the most vulnerable of the three, and you should choose it if you have been sad, and have missed what we had.

Message 2 is more reflective. It is less about simply telling you that I miss you, and more about trying to understand what happened between us. It talks about resentment, our future, my mistakes, the effect of the distance, and what I have come to understand after having some time to think. This contains the most depth, and also mentions what the next months look like for me. Choose this for a down-the-middle, in depth review.

Message 3 is the closure version. It contains many of the same feelings as Message 1, essentially the things I would want you to know if we never spoke again: what I am sorry for, what I appreciate about what we had, and what I hope for you going forward. Choose this if you're ready to move on (or have moved on!).

None of the three is intended to be the "right" choice. They are just three different ways of saying the things I have been carrying around, depending on what you feel most comfortable reading.

Once you choose one, that is the only message you will be able to read. The other two will be permanently locked, so there genuinely isn't a way for me to give you access to them afterwards. So, be careful.

I thought about adding some fun easter eggs, but didn't want to overdo it. A nice colour scheme of sage green and sunset orange, along with the security question (well done on passing) should do it.

There is no pressure to reply, but feel free to reach out.

I really don't know how this will go down - it is quite daunting reaching out and being pretty vulnerable on here. All I know is that things ended so quickly, and I wanted to address a couple of things for good.

Just to let you know, this website will automatically be taken down 24 hours after you choose to open one of the messages. If you wish to respond, take whatever time you need.

Obviously you can copy/paste the message, and do whatever you like, but it would be nice to keep this between us if possible.

"""


# ============================================================
# "I CAN'T CHOOSE" POPUP
# ============================================================

INDECISION_TITLE = "Not sure?"

INDECISION_MESSAGE = """
That's okay. Here's a bit more context to help:

There isn't really a "right" choice.

Message 1 is the most emotional and personal. It is about how I feel now, how much I miss you, and the things I still find difficult about losing you.

Message 2 is the most analytical and reflective. It is about trying to understand why things went wrong, my role in that, what I regret, and what I have thought about our relationship since it ended.

Message 3 is the closure message. It is about saying the things I would want you to know if we never spoke again, without asking anything of you in return.

They overlap, but they are deliberately different in what they focus on.

You will only get to read one, so choose whichever feels most appropriate to you.

And if you genuinely don't want to read any of them, that's okay too.
"""


# ============================================================
# THREE MESSAGES
# ============================================================

MESSAGES = {

    "1": """
Hey Char,

Firstly, I hope you are well. I really do. I hope you had an amazing time at home in Canada, as well as over your Summer break. It has been nice to watch along from a distance and see you enjoying yourself.

I don't know how this message will find you. It may be a terrible idea to contact you, and perhaps one that I should never have opted for. I recognise that perhaps it is too soon, and you would rather time and space. I understand you may be hurt after everything that happened. Equally, perhaps you are happier now, moving forward with life, and finding peace in the distance between us. I really hope the time with your friends and family have left you with a positive mindset and some special memories.

I have tried my best - albeit with limited knowledge of your comings and goings - to time this message such that you will see it after you have left Canada. I do not want to interfere with the time you have with your family - something so special and important.

I understand I was reasonably firm about not wanting to be in contact. In hindsight, I think that this has been beneficial for me. I have needed time to process what happened, and remove myself from the immediacy of everything. I have come to terms with what has happened with a clearer head. I hope, with however you have approached the last couple of months, you also have gained some additional clarity.

I am not writing this message just to bug you, to interrupt your healing, or to elicit a response. I recognise you have no obligation to reply to me. I considered writing a physical letter, partly because I would not know when it had been received, and therefore it would place less immediate pressure on you to respond. In the end, I thought that the four or more weeks it may take for you to receive this, and potentially respond, may not be ideal in an ever-developing dynamic.

I have had a lot of time to think over the last weeks, and have isolated myself to have time to genuinely reflect, rather than seek the opinions of others. So much of what unfolded is so specific to just us, with the history and context that developed over time, that nobody aside from you would ever truly understand my words anyway. My thoughts below are not an attempt to reopen every argument we ever had, but they are instead the thoughts that have stayed with me, and the thoughts that I have come to understand differently, with some reflection. While I recognise it may be unorthodox to send such a lengthy message after months of no contact, I would forever regret not letting you know a couple of things.

I don't really know how to start this, but I think the simplest thing I can say is that I miss you, and I miss what we had.

I miss you in the ways that I knew I would, but also so much more. I miss your voice, and your laugh. I miss calling you, and seeing notifications from you. I miss your touch, and your smell. I miss sleepovers, and the ordinary things that never feel significant until they are gone. I miss listening to music in your kitchen, eating too much Zambreros, and walking Russell together at sunset.

For so long, having you physically elsewhere was something I was learning to manage. It was difficult, and I hated the distance, but you were still my person.

Not having you here was hard, but not having you at all is near-impossible.

You knew me better than anyone, and I never had to explain myself around you. Eventually, I took this for granted, and now there is a strange absence where you used to be.

Life is okay. I am getting on with things. Being so very busy does help, but in the quiet times, at the end of the day, or on a Sunday afternoon, everything is quiet, and it's your voice I wish I could hear the most.

I don't want to make you feel guilty, or responsible for my happiness. You should just understand that losing you hasn't been easy. You'll feel as you read this, that this is a stripped back version of how we both used to feel, and it's because while it is all true, it is difficult to be so vulnerable with someone I haven't spoken to in so long. It is so tough carrying around years of memories and feelings regarding someone I no longer even speak to.

I've thought a lot about why things ended, and I've thought even more about my part in it. I want you to know that I am sorry. I am sorry I wasn't more supportive of your goals, and your aspirations. I understand that these goals took you further away from me, but that was never why you did it. I was just bitter about the distance, and frustrated by what it meant for us, that I was not able to properly celebrate what it meant for you. You deserved to have somebody that was completely proud of you.

I understand I became complacent, and let frustration and resentment live where excitement and affection should have resided. I am also sorry that I didn't tell you that you were loved enough. Part of me assumed you knew, part of me was frustrated, and saying it made the distance feel so much further. It's not an excuse, I should have just told you, as you deserved to hear it.

I don't know exactly how I feel now, but I find myself looking at charporkspriv more often than I'd care to admit, and listening to music that makes me think of you (I saw you saved my playlist). It's so difficult moving on, and I would be lying if I said there wasn't at least a part of me that has wanted to reach out just to hear from you for a while now.

That's part of the reason why I've given you a choice in what you read. I could give you a tidy little goodbye, and move on, or I could break down why we went wrong, like I have in the other messages, but really, I know I miss you, at least a bit, so I might as well tell you.

I'm really proud of you. You are a truly special person, and I am glad you were brave and chased what you wanted to achieve. It is inspiring, and I hope you know that you have always inspired me, ever since we met as kids.

The point of this message is not to elicit a response from you, but to let you know that I miss you, and things aren't easy. You don't owe me anything: not an apology, not forgiveness, and not a response. Writing all three versions of these messages has helped me realise that I apologise for my role in our demise, verbalise how I feel, and move on regardless of how you feel in return.

I hope you are happy, and continue to be happy. Keep being brave each day and go out and get what you want, I am sure you are destined for great things, both personally and professionally. You have always been capable of so much, and I hope you get the best out of life.

P.S.

It was nice (and unexpected) to see your scientific photography entries. Also, I thought you would like these - sometimes I sit for a minute and think about sending you things, but up until now, I always resist.

https://www.instagram.com/reel/DcI-o-2ASa5/

https://www.instagram.com/reel/DcD8jwlkflb/

https://www.instagram.com/p/DZA_VRbCXVN/

There is plenty more I can say, and would like to share with you, but I will leave it there for now. This is just the bare-bones "if we were to never speak again, I would want her to know" explanation. If you have any thoughts, want me to elaborate, or just simply want to hear from me, let me know.
""",

    "2": """
Hey Char,

Firstly, I hope you are well. I really do. I hope you had a lovely time travelling, and also with your family. I think it is special that you got to see them again.

I don't know how this message will find you. It may be a terrible idea to contact you, and perhaps one that I should never have opted for. I recognise that perhaps it is too soon, and you would rather time and space. I understand you may be hurt after everything that happened. Equally, perhaps you are happier now, moving forward with life, and finding peace in the distance between us. I really hope the time with your friends and family have left you with a positive mindset and some special memories.

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

The truth is that I could never envision my life without you, but I never made it known to you. I believe the reason why I never thought we had a shared vision was accelerated by the fact that instead of asking you what you wanted your future to look like, I began to treat the absence of a clearly defined future as evidence that there couldn't be one.

I regret we did not discuss what you wanted your life to look like, and I regret not speaking honestly about what I wanted. We could have seen if these things could have coexisted. Perhaps they could, perhaps they could not. I don't know.

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

In a few months, I will reach somewhat of a crossroads, in which, for the first time ever, I won't be studying, and I have some decisions to make about what the next year(s) will look like. Until recently, I had been pretty set on taking a few months off, and maybe travelling around Australia or overseas before committing to anything long-term, whether it be employment or study.

But, really, I always thought it would be you that I would spend this time with. Pertaining to my previous point, I had a rough vision for us, which I never really got to share with you, as you have been away so often. It gradually became something that seemed increasingly unlikely, and I eventually stopped imagining it. But now, with everything that has happened, I find myself wondering what it could have been like.

I do not know what you plan to do once your internship ends. You have previously mentioned you may look to study, or even work, overseas. Maybe LEGO will want to keep you around. Perhaps you'll come home and stay for a while. Maybe it'll be something completely different, that both you and I couldn't yet imagine. It is your life, and your decision, and I do not want this message to make you feel that you need to make any of those decisions with me in mind.

However, I want to be honest about something. If you do come home in a few months, and with enough time and distance from everything that has happened, you have developed your own thoughts and feelings, I don't want to pretend that you couldn't still be a part of this time.

I don't want a decision from you, or a promise, or for you to come back. I just want you to know that the door is not closed, should the right circumstances arise.

Why I am sending this

Our final conversations happened so quickly, and I have realised that I had left some things on the table, and some thoughts unsaid. I don't want to spend any more time regretting not being clear with you.

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

There is plenty more I can say, and would like to share with you, but I will leave it there for now. This is just the bare-bones "if we were to never speak again, I would want her to know" explanation. If you have any thoughts, want me to elaborate, or just simply want to hear from me, let me know.
""",

    "3": """
Hey Char,

Firstly, I hope you are well. I really do. I hope you had an amazing time at home in Canada, as well as over your Summer break. It has been nice to watch along from a distance and see you enjoying yourself.

I don't know how this message will find you. It may be a terrible idea to contact you, and perhaps one that I should never have opted for. I recognise that perhaps it is too soon, and you would rather time and space. I understand you may be hurt after everything that happened. Equally, perhaps you are happier now, moving forward with life, and finding peace in the distance between us. I really hope the time with your friends and family have left you with a positive mindset and some special memories.

I have tried my best - albeit with limited knowledge of your comings and goings - to time this message such that you will see it after you have left Canada. I do not want to interfere with the time you have with your family - something so special and important.

I understand I was reasonably firm about not wanting to be in contact. In hindsight, I think that this has been beneficial for me. I have needed time to process what happened, and remove myself from the immediacy of everything. I have come to terms with what has happened with a clearer head. I hope, with however you have approached the last couple of months, you also have gained some additional clarity.

I am not writing this message just to bug you, to interrupt your healing, or to elicit a response. I recognise you have no obligation to reply to me. I considered writing a physical letter, partly because I would not know when it had been received, and therefore it would place less immediate pressure on you to respond. In the end, I thought that the four or more weeks it may take for you to receive this, and potentially respond, may not be ideal in an ever-developing dynamic.

I have had a lot of time to think over the last weeks, and have isolated myself to have time to genuinely reflect, rather than seek the opinions of others. So much of what unfolded is so specific to just us, with the history and context that developed over time, that nobody aside from you would ever truly understand my words anyway. My thoughts below are not an attempt to reopen every argument we ever had, but they are instead the thoughts that have stayed with me, and the thoughts that I have come to understand differently, with some reflection. While I recognise it may be unorthodox to send such a lengthy message after months of no contact, I would forever regret not letting you know a couple of things.

I don't really know how to start this, but I think the simplest thing I can say is that I miss you, and I miss what we had.

I miss you in the ways that I knew I would, but also so much more. I miss your voice, and your laugh. I miss calling you, and seeing notifications from you. I miss your touch, and your smell. I miss sleepovers, and the ordinary things that never feel significant until they are gone. I miss listening to music in your kitchen, eating too much Zambreros, and walking Russell together at sunset.

For so long, having you physically elsewhere was something I was learning to manage. It was difficult, and I hated the distance, but you were still my person.

Not having you here was hard, but not having you at all is near-impossible.

You knew me better than anyone, and I never had to explain myself around you. Eventually, I took this for granted, and now there is a strange absence where you used to be.

Life is okay. I am getting on with things. Being so very busy does help, but in the quiet times, at the end of the day, or on a Sunday afternoon, everything is quiet, and it's your voice I wish I could hear the most.

I don't want to make you feel guilty, or responsible for my happiness. You should just understand that losing you hasn't been easy. You'll feel as you read this, that this is a stripped back version of how we both used to feel, and its because while it is all true, it is difficult to be so vulnerable with someone I haven't spoken to in so long. It is so tough carrying around years of memories and feelings regarding someone I no longer even speak to.

I've thought a lot about why things ended, and I've thought even more about my part in it. I want you to know that I am sorry. I am sorry I wasn't more supportive of your goals, and your aspirations. I understand that these goals took you further away from me, but that was never why you did it. I was just bitter about the distance, and frustrated by what it meant for us, that I was not able to properly celebrate what it meant for you. You deserved to have somebody that was completely proud of you.

I understand I became complacent, and let frustration and resentment live where excitement and affection should have resided. I am also sorry that I didn't tell you that you were loved enough. Part of me assumed you knew, part of me was frustrated, and saying it made the distance feel so much further. It's not an excuse, I should have just told you, as you deserved to hear it.

I don't know exactly how I feel now, but I find myself looking at charporkspriv more often than I'd care to admit, and listening to music that makes me think of you (I saw you saved my playlist). It's so difficult moving on, and I would be lying if I said there wasn't at least a part of me that has wanted to reach out just to hear from you for a while now.

That's part of the reason why I've given you a choice in what you read. I could give you a tidy little goodbye, and move on, or I could break down why we went wrong, like I have in the other messages, but really, I know I miss you, at least a bit, so I might as well tell you.

I'm really proud of you. You are a truly special person, and I am glad you were brave and chased what you wanted to achieve. It is inspiring, and I hope you know that you have always inspired me, ever since we met as kids.

The point of this message is not to elicit a response from you, but to let you know that I miss you, and things aren't easy. You don't owe me anything: not an apology, not forgiveness, and not a response. Writing all three versions of these messages has helped me realise that I apologise for my role in our demise, verbalise how I feel, and move forward, regardless of how you feel in return.

I hope you are happy, and continue to be happy. Keep being brave each day and go out and get what you want, I am sure you are destined for great things, both personally and professionally. You have always been capable of so much, and I hope you get the best out of life.

P.S.

It was nice (and unexpected) to see your scientific photography entries. Also, I thought you would like these - sometimes I sit for a minute and think about sending you things, but up until now, I always resist.

https://www.instagram.com/reel/DcI-o-2ASa5/

https://www.instagram.com/reel/DcD8jwlkflb/

https://www.instagram.com/p/DZA_VRbCXVN/

There is plenty more I can say, and would like to share with you, but I will leave it there for now. This is just the bare-bones "if we were to never speak again, I would want her to know" explanation. If you have any thoughts, want me to elaborate, or just simply want to hear from me, let me know.
"""
}


# ============================================================
# STATE MANAGEMENT
# ============================================================

def get_state():

    if os.path.exists(STATE_FILE):

        try:

            with open(
                STATE_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                state = json.load(f)

                # Make sure older state files still work.
                state.setdefault(
                    "chosen_option",
                    None
                )

                state.setdefault(
                    "authenticated",
                    False
                )

                state.setdefault(
                    "first_visit_at",
                    None
                )

                state.setdefault(
                    "visit_count",
                    0
                )

                return state

        except Exception as e:

            print(
                "Could not read state:",
                e
            )

    return {
        "chosen_option": None,
        "authenticated": False,
        "first_visit_at": None,
        "visit_count": 0
    }


def save_state(state):

    temp_file = STATE_FILE + ".tmp"

    with open(
        temp_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            state,
            f,
            indent=2
        )

        f.flush()

        os.fsync(
            f.fileno()
        )

    os.replace(
        temp_file,
        STATE_FILE
    )


# ============================================================
# HTML
# ============================================================

HTML_TEMPLATE = """
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<title>My Thoughts</title>

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

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

* {
    box-sizing: border-box;
}

html {
    height: 100%;
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

    min-height: 100vh;

    background-color: var(--bg-color);

    position: relative;

    overflow-x: hidden;
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

    margin: 0 auto;

    box-shadow:
        0 10px 30px rgba(44, 53, 49, 0.06);

    border:
        1px solid rgba(129, 178, 154, 0.2);
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

    background-color: #f8fafc;

    color: var(--text-main);

    outline: none;
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
}

.envelope-btn:hover:not(:disabled) {
    background-color: var(--accent-hover);
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


/* ==========================================================
   MESSAGE SCROLL AREA

   This is deliberately an independent scrolling container.
   ========================================================== */

#result {
    margin-top: 25px;

    padding: 20px;

    background-color: #f7f9f7;

    border-left:
        4px solid var(--accent-active);

    border-radius: 8px;

    text-align: left;

    word-break: break-word;

    border-top:
        1px solid rgba(129, 178, 154, 0.15);

    border-right:
        1px solid rgba(129, 178, 154, 0.15);

    border-bottom:
        1px solid rgba(129, 178, 154, 0.15);

    max-height: 60vh;

    overflow-y: auto;

    overscroll-behavior: contain;

    -webkit-overflow-scrolling: touch;

    scrollbar-width: thin;
}

#result p {
    color: var(--text-main);

    line-height: 1.7;

    white-space: pre-wrap;

    margin-top: 8px;

    margin-bottom: 0;
}

#result::-webkit-scrollbar {
    width: 8px;
}

#result::-webkit-scrollbar-track {
    background: transparent;
}

#result::-webkit-scrollbar-thumb {
    background:
        rgba(101, 116, 107, 0.35);

    border-radius: 10px;
}

.hidden {
    display: none !important;
}


/* ==========================================================
   MODALS
   ========================================================== */

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


<div class="card">

    <h2>Choose Wisely</h2>


    <!-- AUTHENTICATION -->

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

            <button onclick="verifyAnswer()">
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


    <!-- CHOICE -->

    <div id="choice-section" class="hidden">

        <p id="status">
            Well done! You are free to select a message now :)
        </p>


        <div class="button-group">

            <button
                id="btn1"
                class="envelope-btn"
                onclick="requestChoice('1')"
            >
                <span>\u2709\ufe0f</span>
                <span>Message 1</span>
            </button>


            <button
                id="btn2"
                class="envelope-btn"
                onclick="requestChoice('2')"
            >
                <span>\u2709\ufe0f</span>
                <span>Message 2</span>
            </button>


            <button
                id="btn3"
                class="envelope-btn"
                onclick="requestChoice('3')"
            >
                <span>\u2709\ufe0f</span>
                <span>Message 3</span>
            </button>

        </div>


        <button
            id="indecision-btn"
            class="secondary"
            style="margin-top: 12px;"
            onclick="showIndecision()"
        >
            I can't choose
        </button>


        <div
            id="result"
            class="hidden"
        ></div>

    </div>

</div>


<!-- INTRO MODAL -->

<div
    id="intro-modal"
    class="modal-overlay hidden"
>

    <div class="modal-box">

        <div class="modal-header">
            <h2>{{ intro_title }}</h2>
        </div>

        <div
            class="modal-body"
            id="intro-body"
        ></div>

        <div class="modal-footer">

            <button
                id="intro-continue-btn"
                onclick="closeIntro()"
            >
                I've read this
            </button>

        </div>

    </div>

</div>


<!-- CONFIRMATION -->

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
                Make sure this is the right one.
            </p>

        </div>

        <div class="modal-footer">

            <button
                id="confirm-yes-btn"
                onclick="confirmChoice()"
                disabled
            >
                Yes, I'm sure
            </button>

            <button
                class="secondary"
                onclick="cancelChoice()"
            >
                Wait, not yet
            </button>

        </div>

    </div>

</div>


<!-- INDECISION -->

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

        <div class="modal-body">
            {{ indecision_message }}
        </div>

        <div class="modal-footer">

            <button onclick="closeIndecision()">
                Okay
            </button>

        </div>

    </div>

</div>


<script>

/* ==========================================================
   PARTICLES
   ========================================================== */

(function() {

    const canvas =
        document.getElementById(
            "particle-canvas"
        );

    if (!canvas) return;

    const ctx =
        canvas.getContext("2d");

    if (!ctx) return;

    let width;
    let height;
    let particles = [];

    const colors = [
        "#81b29a",
        "#e07a5f",
        "#a8c4b4",
        "#eba488"
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
                    Math.random() * width,

                y:
                    Math.random() * height,

                vx:
                    (Math.random() - 0.5) * 0.4,

                vy:
                    (Math.random() - 0.5) * 0.4,

                r:
                    Math.random() * 2.5 + 2,

                color:
                    colors[
                        Math.floor(
                            Math.random() *
                            colors.length
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


        for (const p of particles) {

            p.x += p.vx;
            p.y += p.vy;


            if (p.x < -10)
                p.x = width + 10;

            if (p.x > width + 10)
                p.x = -10;

            if (p.y < -10)
                p.y = height + 10;

            if (p.y > height + 10)
                p.y = -10;


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
                        (dx / dist) *
                        force;

                    p.y +=
                        (dy / dist) *
                        force;
                }
            }


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

            ctx.globalAlpha =
                0.8;

            ctx.fill();
        }


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
                        "rgba(129, 178, 154, " +
                        (
                            0.35 *
                            (1 - dist / 130)
                        ) +
                        ")";

                    ctx.lineWidth = 1.2;

                    ctx.stroke();
                }
            }
        }


        requestAnimationFrame(step);
    }


    window.addEventListener(
        "resize",
        () => {
            resize();
            initParticles();
        }
    );


    window.addEventListener(
        "mousemove",
        e => {

            mouse.x =
                e.clientX;

            mouse.y =
                e.clientY;

            mouse.active = true;
        }
    );


    window.addEventListener(
        "mouseleave",
        () => {
            mouse.active = false;
        }
    );


    window.addEventListener(
        "touchmove",
        e => {

            if (e.touches.length > 0) {

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
        "touchend",
        () => {
            mouse.active = false;
        }
    );


    resize();
    initParticles();
    step();

})();


/* ==========================================================
   GLOBAL STATE
   ========================================================== */

let introShown = false;

let pendingChoice = null;

/*
 * VERY IMPORTANT:
 *
 * This variable prevents checkState() from recreating
 * the message every three seconds.
 *
 * Recreating the message was what caused the scrollbar
 * to jump back to the top.
 */
let renderedChoice = null;


/* ==========================================================
   INTRO
   ========================================================== */

function typewriteIntro() {

    const el =
        document.getElementById(
            "intro-body"
        );

    el.textContent =
        {{ intro_message|tojson }};
}


function showIntroOrChoice() {

    if (!introShown) {

        document
            .getElementById("intro-modal")
            .classList
            .remove("hidden");

        typewriteIntro();

    } else {

        document
            .getElementById("choice-section")
            .classList
            .remove("hidden");
    }
}


function closeIntro() {

    introShown = true;

    document
        .getElementById("intro-modal")
        .classList
        .add("hidden");

    document
        .getElementById("choice-section")
        .classList
        .remove("hidden");
}


/* ==========================================================
   INDECISION
   ========================================================== */

function showIndecision() {

    document
        .getElementById("indecision-modal")
        .classList
        .remove("hidden");
}


function closeIndecision() {

    document
        .getElementById("indecision-modal")
        .classList
        .add("hidden");
}


/* ==========================================================
   AUTHENTICATION
   ========================================================== */

async function verifyAnswer() {

    const input =
        document.getElementById(
            "answer-input"
        );

    const answer =
        input.value;


    try {

        const res =
            await fetch(
                "/verify",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
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
                .getElementById(
                    "auth-section"
                )
                .classList
                .add("hidden");

            showIntroOrChoice();

        } else {

            document
                .getElementById(
                    "error-msg"
                )
                .classList
                .remove("hidden");

            input.value = "";
        }

    } catch (e) {

        console.error(e);

    }
}


function handleKeyPress(e) {

    if (e.key === "Enter") {

        verifyAnswer();

    }
}


/* ==========================================================
   CHOICE
   ========================================================== */

function requestChoice(option) {

    pendingChoice = option;


    const yesBtn =
        document.getElementById(
            "confirm-yes-btn"
        );


    yesBtn.disabled = true;


    document
        .getElementById(
            "confirm-modal"
        )
        .classList
        .remove("hidden");


    let secondsLeft = 5;


    yesBtn.innerText =
        `Yes, I'm sure (${secondsLeft})`;


    const countdown =
        setInterval(
            () => {

                secondsLeft -= 1;


                if (secondsLeft > 0) {

                    yesBtn.innerText =
                        `Yes, I'm sure (${secondsLeft})`;

                } else {

                    clearInterval(
                        countdown
                    );

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

    document
        .getElementById(
            "confirm-yes-btn"
        )
        .innerText =
        "Yes, I'm sure";

    document
        .getElementById(
            "confirm-modal"
        )
        .classList
        .add("hidden");
}


/* ==========================================================
   CONFIRM CHOICE
   ========================================================== */

async function confirmChoice() {

    if (!pendingChoice)
        return;


    const option =
        pendingChoice;


    document
        .getElementById(
            "confirm-modal"
        )
        .classList
        .add("hidden");


    try {

        const res =
            await fetch(
                "/choose",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
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

        alert(
            "Network error. Please try again."
        );

        checkState();
    }


    pendingChoice = null;
}


/* ==========================================================
   LOCK + DISPLAY MESSAGE
   ========================================================== */

function applyLock(chosen, msg) {

    /*
     * Hide indecision button.
     */

    document
        .getElementById(
            "indecision-btn"
        )
        .classList
        .add("hidden");


    /*
     * Lock all buttons.
     */

    document
        .querySelectorAll(
            "#choice-section .envelope-btn"
        )
        .forEach(
            (button, index) => {

                button.disabled = true;

                const number =
                    String(index + 1);

                const label =
                    button.querySelectorAll(
                        "span"
                    )[1];


                if (number === chosen) {

                    button.style.backgroundColor =
                        "var(--accent-active)";

                    label.textContent =
                        `Message ${chosen} (Opened)`;

                } else {

                    label.textContent =
                        `Message ${number} (Locked)`;
                }
            }
        );


    document
        .getElementById("status")
        .innerText =
        "Choice permanently registered on server. Other options are locked.";


    /*
     * ======================================================
     * CRITICAL SCROLL FIX
     * ======================================================
     *
     * If this message has already been rendered, DO NOTHING.
     *
     * checkState() runs every 3 seconds.
     * Previously it was rebuilding #result every time.
     * That reset scrollTop to 0.
     *
     * Now the DOM is only constructed once.
     */

    if (renderedChoice === chosen) {
        return;
    }


    renderedChoice = chosen;


    const resBox =
        document.getElementById(
            "result"
        );


    resBox.classList.remove(
        "hidden"
    );


    resBox.innerHTML = "";


    const heading =
        document.createElement(
            "strong"
        );


    heading.style.color =
        "var(--accent-color)";

    heading.textContent =
        "Message " + chosen + ":";


    const message =
        document.createElement(
            "p"
        );


    message.textContent =
        msg;


    resBox.appendChild(
        heading
    );

    resBox.appendChild(
        message
    );
}


/* ==========================================================
   SERVER STATE
   ========================================================== */

async function checkState() {

    try {

        const res =
            await fetch(
                "/status?" +
                Date.now()
            );


        const data =
            await res.json();


        if (data.chosen_option) {

            document
                .getElementById(
                    "auth-section"
                )
                .classList
                .add("hidden");


            document
                .getElementById(
                    "intro-modal"
                )
                .classList
                .add("hidden");


            document
                .getElementById(
                    "confirm-modal"
                )
                .classList
                .add("hidden");


            document
                .getElementById(
                    "indecision-modal"
                )
                .classList
                .add("hidden");


            document
                .getElementById(
                    "choice-section"
                )
                .classList
                .remove("hidden");


            applyLock(
                data.chosen_option,
                data.message
            );


        } else if (
            data.authenticated
        ) {

            document
                .getElementById(
                    "auth-section"
                )
                .classList
                .add("hidden");

            showIntroOrChoice();
        }

    } catch (e) {

        console.error(e);

    }
}


/*
 * Initial state check.
 */

checkState();


/*
 * Poll server state every 3 seconds.
 *
 * IMPORTANT:
 * This does NOT generate notifications.
 *
 * Only visiting "/" generates a visit notification.
 */

setInterval(
    checkState,
    3000
);

</script>

</body>

</html>
"""


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def home():

    state = get_state()

    current_time = now_adelaide()

    first_visit = parse_time(
        state.get(
            "first_visit_at"
        )
    )


    # ========================================================
    # RECORD FIRST VISIT
    # ========================================================

    if first_visit is None:

        first_visit = current_time

        state["first_visit_at"] = iso_time(current_time)

    state["first_visit_at"] = iso_time(
        first_visit
    )


    # ========================================================
    # INCREMENT VISIT COUNT
    # ========================================================

    state["visit_count"] = (
        state.get(
            "visit_count",
            0
        ) + 1
    )


    save_state(state)


    visit_number = state["visit_count"]


    elapsed = (
        current_time -
        first_visit
    ).total_seconds()


    # ========================================================
    # NOTIFY EVERY TIME "/" IS VISITED
    # ========================================================

    if visit_number == 1:

        visit_message = (
            "\U0001F517 CHAR MESSAGES \u2014 FIRST VISIT\n\n"
            f"Time: {formatted_time(current_time)}\n"
            f"Visit number: {visit_number}\n\n"
            "The link has been opened for the first time."
        )

    else:

        visit_message = (
            "\U0001F517 CHAR MESSAGES \u2014 LINK VISITED\n\n"
            f"Time: {formatted_time(current_time)}\n"
            f"Visit number: {visit_number}\n"
            f"Time since first visit: "
            f"{format_elapsed(elapsed)}\n\n"
            "The link has been opened again."
        )


    send_notification(
        visit_message
    )


    return render_template_string(

        HTML_TEMPLATE,

        question=
            SECURITY_QUESTION,

        image_url=
            SECURITY_IMAGE_URL,

        intro_title=
            INTRO_TITLE,

        intro_message=
            INTRO_MESSAGE,

        indecision_title=
            INDECISION_TITLE,

        indecision_message=
            INDECISION_MESSAGE
    )


# ============================================================
# STATUS
# ============================================================

@app.route(
    "/status",
    methods=["GET"]
)
def status():

    state = get_state()

    chosen = state.get("chosen_option")

    authenticated = state.get(
        "authenticated",
        False
    )


    if chosen:

        return jsonify({

            "chosen_option":
                chosen,

            "message":
                MESSAGES[chosen],

            "authenticated":
                True
        })


    return jsonify({

        "chosen_option":
            None,

        "authenticated":
            authenticated
    })


# ============================================================
# VERIFY
# ============================================================

@app.route(
    "/verify",
    methods=["POST"]
)
def verify():

    req_data = request.get_json(
        silent=True
    ) or {}

    user_answer = req_data.get(
        "answer",
        ""
    ).strip().lower()

    accepted = [
        answer.lower()
        for answer in ACCEPTED_ANSWERS
    ]


    if user_answer in accepted:

        state = get_state()

        state["authenticated"] = True

        save_state(state)


        return jsonify({
            "success": True
        })


    return jsonify({
        "success": False
    }), 400


# ============================================================
# CHOOSE
# ============================================================

@app.route(
    "/choose",
    methods=["POST"]
)
def choose():

    state = get_state()


    # --------------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------------

    if not state.get(
        "authenticated",
        False
    ):

        return jsonify({

            "success": False,

            "error":
                "Not authenticated!"

        }), 403


    # --------------------------------------------------------
    # PREVENT SECOND CHOICE
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # VALID CHOICE
    # --------------------------------------------------------

    if choice not in MESSAGES:

        return jsonify({

            "success": False,

            "error":
                "Invalid choice"

        }), 400


    # --------------------------------------------------------
    # RECORD CHOICE
    # --------------------------------------------------------

    current_time = now_adelaide()


    first_visit = parse_time(
        state.get(
            "first_visit_at"
        )
    )


    elapsed_text = "unknown"


    if first_visit:

        elapsed_seconds = (
            current_time -
            first_visit
        ).total_seconds()

        elapsed_text = format_elapsed(
            elapsed_seconds
        )


    state["chosen_option"] = choice


    state["chosen_at"] = iso_time(
        current_time
    )


    save_state(state)


    # --------------------------------------------------------
    # CHOICE NOTIFICATION
    # --------------------------------------------------------

    notification = (
        "\U0001F48C CHAR MESSAGES \u2014 CHOICE MADE\n\n"
        f"Time: {formatted_time(current_time)}\n"
        f"Message opened: {choice}\n"
        f"Time since first visit: {elapsed_text}\n"
        f"Total visits to link: "
        f"{state.get('visit_count', 0)}\n\n"
        "She has made her choice."
    )


    send_notification(
        notification
    )


    return jsonify({

        "success":
            True,

        "message":
            MESSAGES[choice]
    })


# ============================================================
# RESET
# ============================================================

@app.route(
    "/reset"
)
def reset_state():

    if os.path.exists(
        STATE_FILE
    ):

        os.remove(
            STATE_FILE
        )


    return (
        "State has been reset!"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

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
