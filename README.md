# Fill-in-the-blank-generator

**I needed to memorise a text by heart, but I didn't feel like repeating over and over everytime,** and wanted to switch study methods for something new. <br>
I realised that using fill in the blanks exercises would be a good way to test my knowledge and understanding of the said text. <br>
I also wanted the difficulty of the exercise to increase progressively, few blanks at the start, and few words at the end of the study session. <br>
I searched on the internet for some fill-in-the-blanks generators but they were all lucrative.
<br><br>


In French, we have a saying : *"On n'est jamais mieux servi que par soi-même"* which can be translated as "You are never as well served as when you serve yourself'.
**I decided that I would make my own fill-in-the-blank generator.** Here's the features I wanted.

- Ability to copy-paste from a source
- Ability to choose how much of the words I wanted to be hidden (percentage).
- Ability to reveal the whole text after studying, to correct myself
 <br><br>


I needed it done quickly so I chose a language that I'm familiar with and a library that I worked on several times before : Python and Pygame.
Even though Pygame is not the best for Graphic-User-Interface, I mananged to use it, with POO.
Here's the architecture : 
```
├── src
│   ├── button.py
│   ├── constants.py
│   ├── main.py
│   ├── slider.py
│   ├── text_display.py
│   └── text_input_box.py
└── assets
    └── fonts
        ├── Capriola-Regular.ttf
        └── OFL.txt
```
I used the font Capriola-Regular, which is free for personal use. <br>
<br><br>


I know have a wotking fill-in-the-blank generator, that I use when studying. **I use it especially when I need to make sure that I understand a concept and that it is well memorised**. I really appreciate the feature of being able to choose how much of the words are hidden as it allows me to choose the difficulty depending on what stage of studying I'm at. If you have ideas for other features, let me know ! I hope you enjoy the software !
