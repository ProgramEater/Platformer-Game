Open "Level editor.exe" to open level editor.

There you can ||DRAW|| any tile by clicking and holding left mouse button and dragging it across the screen.
You can ||ERASE|| tiles by doing the same but holding -right- mouse button.

You can ||CHOOSE ANOTHER TILE|| from ones that are displayed. To do so, click on the tile to choose one.
Above every tile that you can choose there is a text or a symbol. 
This is the symbol of the tile that defines it in .csv table with level map

There is also a "special" tile that you can choose (there is a word "special" above it ._.)
When you try to draw with that it should ask you for input.
Whatever you write in the console will be in the corresponding cell in .csv table with the level map

to see what is the symbol of any tile 
	simply place a cursor above the tile which name you want to know. 
	Its name will be diaplyed UNDER a board (with tiles)

To ||SAVE|| or ||OPEN|| a level click the corresponding button (save or open), 
	then open a console and follow the instructions

To ||CHANGE SIZE|| of board, tiles or resolution 
	click a square button to the right of "save" and "open" button and follow the instructions.

+------------------------------------------------------------------------------------------------------------+

If you want to change other interface parameters:
	go to "Level_Editor_modules/data/json_params/params.json", please don't break it, it wouldn't work that way

If you want to add more tiles or delete or change already existing ones:
	go to "Level_Editor_modules/data/json_params/tiles_images.json". There is dict. 
		Keys of the dict is the symbol that defines the tile in .csv table in a level map.
		Values are the path to the tile texture you want it to have. 
		If the texture doesn't exist, tile would have pink color
		(You can store textures in "Level_Editor_modules/data/textures/" for convenience
