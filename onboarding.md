# ONBOARDING - User Route

## First Text
- User add the bot the its Telegram contact `@SUTD_coffree_bot`
- User received a text: "Hey Remi, I’m Coffree. ☕
I help you find the best free coffee stop before your next class. 
Where are you heading next ?

After this text, the user will have to chose from 4 different options (button):
1. Building 1
2. Building 2
3. Level 4 and above
4. Give me the coffee location 'lready!

### User clicks 1 | 2 | 3
Bot provide a simple answer following this format: "You can grab your free coffee here in `location.json.class_id, class.name,class.building, class.level, class.photo_folder.first_photo` ☕
Recommended timing: 9:15am onwards.

Tap “Where is this?” if you want help finding the room.

User has the option to click 'get directions to this class' or have the option 'get all coffee locations'

### User clicks 4
Bot provide a list of the locations that follow the json format for all the locations with coffee today. make sure to separate the locations with bullet points and white space in between to ul-li.

- `class.class_id: class.name class.building class.level (class.hint_1) `

- `class.class_id: class.name class.building class.level (class.hint_1) `

- `class.class_id: class.name class.building class.level (class.hint_1) `

- `class.class_id: class.name class.building class.level (class.hint_1) `

User has multiple options at this point (represented as button)

- need directions details for `option 1`
- need directions details for `option 2`
- need directions details for `option 3`
- need directions details for `option 4`

If one of this option is clicked, all the photos in the class-direction-photo-`option x` will be shown in a specific order as it has to follow directions:
-  photo order for building 1 classes:
- IMG_2300.JPG
- next IMG_xxxx.JPG (ascending order)
- last pic: buffet.png

- photo order for building 2 classes:
- Ascending order and buffer.png


after the sequence of photo being send a text is displayed:
"Enjoy your Free Coffee,
Coffree. :coffee emoji::"

## Daily Text
- User receives a text at 8:15 a.m saying "Good mornig {name}, do you want me to check for free coffee today ?"

1. *click* YES
2. *click* NO


1. `option a` `option b`
User has 3 options to click:
Direction to 'a'|Direction to 'b' | more coffee locations

- more coffee location will go on the same path as for ### User clicks 4

2. "Alright, have a good day !"

