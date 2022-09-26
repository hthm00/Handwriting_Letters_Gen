class Gcode_Gen:
    def __init__(self):
        # instance fields found by C# to Python Converter:
        self._minUnitsLineSpacingRandomize = -1
        self._maxUnitsLineSpacingRandomize = -1
        self._moveCoordSettings = "-1,-1"
        self._lineGoingDownCoefficient = 0
        self._symbolSizeRandomizer = -1
        self._rendercount = 0
        self._h_height = 0
        self._h_char_count = 0
        self._h_font_map = ""
        self._font_chars = [[] for _ in range(2000)]
        self._last_filename = ""
        self._appfault = False
        self._preview_mag = 2
        self._shouldBeRotated = False
        self._minRotate = int(5)
        self._maxRotate = int(15)
        self._incorrectLetterChance = 0.0

    def _load_font(self, fname):
        counter = 0
        line = None

        charcount = 0
        # /Users/macos/PycharmProjects/Handwritten_Letters_Gen/GCodeGenerator/GCodeGenerator/fonts/cursive.cmf
        file = open("/Users/macos/PycharmProjects/Handwritten_Letters_Gen/GCodeGenerator/GCodeGenerator/fonts/" +
                    fname + ".cmf", mode='r', encoding='utf-8-sig')
        lines = file.readlines()
        for line in lines:
            line = line.rstrip("\n")
            print(line)
            if (line is not None):  # iterate through the font file
                if counter == 0:
                    # first line: Character count
                    self._h_char_count = float(line)
                if counter == 1:
                    # second line: Character height
                    self._h_height = float(line)
                if counter == 2:
                    self._h_font_map = " " + line  # third line: Character map
                if counter > 2:
                    # each line consists of width, realwidth, arraysize, [x/y pairs]    //arraysize is unused   //??
                    temparray = line.split(',')
                    self._font_chars[charcount] = [
                        0 for _ in range(len(temparray))]
                    idx = 0
                    while idx < len(temparray):
                        self._font_chars[charcount][idx] = temparray[idx]
                        idx += 1
                    charcount += 1
                counter += 1
        file.close()

        print(self._font_chars)
        # update_font_size()

    def _render_stuff(self, saving, tb_input_Text):
        FontComboBox_Text = "cursive"
        lbl_font_height_Text = "10"
        bedwidth_Text = "220"
        beddepth_Text = "220"
        offsetx_Text = "50"
        offsety_Text = "20"
        penup_Text = "0.4"
        pendown_Text = "0.2"
        tspeed_Text = "200"
        dspeed_Text = "200"
        zspeed_Text = "200"
        lspacing_Text = "20"
        letspacing_Text = "1.7"
        # tb_input_Text = """Jacquelyn Fuller
# 2323 Country Club Dr
# Pearland, TX 77581"""
        fontscale_value_Text = "0.27027027027027"

        GX = 0
        GY = 0
        accum_x = 0
        accum_y = 0

        scale = float(fontscale_value_Text) / 5  # get the font scale
        char_height = self._h_height * scale  # scale up the character height
        line_spacing = float(lspacing_Text) * scale * \
            5  # scale up the line spacing
        letter_spacing = float(letspacing_Text) * scale * \
            5  # scale up the letter spacing
        # align text with edge of bed

        offx = float(offsetx_Text)  # get the X Offset from the UI
        offy = float(offsety_Text)  # get the Y Offset from the UI

        out_of_bounds = False  # init a boolean for general plotting fault

        max_x = float(bedwidth_Text)  # get the Bed X setting from the UI
        max_y = float(beddepth_Text)  # get the Bed Y setting from the UI

        # get the Draw speed setting from the UI
        F_draw = int(dspeed_Text) * 60
        # get the Travel speed setting from the UI
        F_travel = int(tspeed_Text) * 60
        # get the Z-Axis speed setting from the UI
        F_zspeed = int(zspeed_Text) * 60
        first_move = True

        lastx = 0  # keep track of where we were for pen up/pen down test
        lasty = 0

        output = ""

        #toolStripStatusLabel3.Text = "Rendering...Please wait"
        # new
        textSize_tb_Text = "{:.2f}".format(
            float(fontscale_value_Text) * 0.37 * 100)
        font_offset_y = float(textSize_tb_Text)  # align text with edge of bed
        #

        # write current settings to file for debug and consistency
        output += "; Font: " + FontComboBox_Text + "\r\n"
        output += "; FontScale: " + textSize_tb_Text + \
            "mm (" + str(scale) + ")\r\n"
        output += "; Bed: " + bedwidth_Text + " x " + beddepth_Text + "\r\n"
        output += "; Offset: " + offsetx_Text + " x " + offsety_Text + "\r\n"
        output += "; Draw mode: " + "Pen" + "\r\n"
        output += "; Pen Up: " + penup_Text + "\r\n"
        output += "; Pen Down: " + pendown_Text + "\r\n"
        output += "; Travel speed: " + tspeed_Text + "\r\n"
        output += "; Draw speed: " + dspeed_Text + "\r\n"
        output += "; Z speed: " + zspeed_Text + "\r\n"
        output += "; Line Spacing: " + lspacing_Text + "\r\n"
        output += "; Letter spacing: " + letspacing_Text + "\r\n"
        output += "; Text input...\r\n; ----\r\n;\t" + \
            (tb_input_Text.replace("\r\n", "\r\n;\t")) + "\r\n; ---- \r\n"

        output += "G21" + "\r\n"  # set units to millimeters

        output += "G0 Z" + penup_Text + " F" + \
            str(F_travel) + "\r\n"  # Pen up before any moves

        symbolMovingError = False

        # //////////////
        randomLineSpacingCheckbox_Checked = True
        lineGoingDownCheckbox_Checked = False
        correctLettersCheckbox_Checked = False
        rotCheckbox_Checked = True
        differentSizeCheckbox_Checked = False
        connectLettersCheckBox_Checked = False

        # /////////////////

        # split the text input up in to lines
        lines = tb_input_Text.split("\n")
        print(lines)
        for thisline in lines:  # interate through the lines
            # function to increase/decrease line spacing randomly
            if randomLineSpacingCheckbox_Checked and not (self._minUnitsLineSpacingRandomize == -1 or self._maxUnitsLineSpacingRandomize == -1):
                line_spacing = ((float(random.randint(int((self._minUnitsLineSpacingRandomize * 100)),
                                int((self._maxUnitsLineSpacingRandomize * 100)) - 1))) / 100) * scale * 5
            prevOutputPointX = -1
            prevOutputPointY = -1
            correctedLetter = False
            prevCorrectedLetter = False
            a = 0
            while a < len(thisline):  # interate through each character of the line
                lineFactor = 0
                if lineGoingDownCheckbox_Checked:  # Line going down
                    # 70 is average symbol width - count it as is not to spend time on counting width sum
                    maxSymbolsInTheLine = int(
                        ((max_x - offx) / (70 * 2.5 * scale)))
                    # TODO: make the line going down not by amount of words but by its width
                    lineFactor = (self._lineGoingDownCoefficient /
                                  maxSymbolsInTheLine) * a
                # this bool is used to clear the output point valuee if it is not found
                ifOuputPointFound = False
                xFactor = 0.0  # Random character movement modifier is here.
                yFactor = 0.0
                multX = 0
                multY = 0

                # init cnum - this string is a map of the font. the index of the character aligns with the font_chars array for the character data.
                # Language other than english won't map correctly here.// Actually it would after you implemented new cmf format. I am here because i want the cyrillic support :D (snow4dv)
                # int cnum = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~".IndexOf(thisline.Substring(a, 1)); //font map is now read from the cmf font file
                cnum = 0
                valid = True
                thewidth = 0
                try:
                    # check to see if we have that character and if >1  - getting random of ones we have
                    indexes = []
                    iter = 0
                    while iter < len(self._h_font_map):
                        if self._h_font_map[iter] == thisline[a:a + 1]:
                            indexes.append(iter)
                        iter += 1

                    cnum = int(indexes[random.randint(0, len(indexes) - 1)])
                    # double thewidth = Convert.ToInt32(font_chars[cnum][0]);         //gets the character width (0)
                    # gets the character real width (1)
                    thewidth = int(self._font_chars[cnum][1])
                except Exception as excep:
                    valid = False

                # checking if letter is going to be wrong and corrected
                if (random.uniform(0, 1) <= self._incorrectLetterChance) and correctLettersCheckbox_Checked and (not prevCorrectedLetter) and valid:
                    correctedLetter = True
                    prevCorrectedLetter = True
                    lineNum = random.randint(0, len(lines) - 1)
                    symbolNum = random.randint(0, len(lines[lineNum]) - 1)
                    randChar = lines[lineNum][symbolNum]
                    indexes = []
                    iter = 0
                    while iter < len(self._h_font_map):
                        if self._h_font_map.ToCharArray()[iter] == randChar:
                            indexes.append(iter)
                        iter += 1

                    cnum = int(indexes[random.randint(0, len(indexes) - 1)])
                    # double thewidth = Convert.ToInt32(font_chars[cnum][0]);         //gets the character width (0)
                    # if correctedSymbol and its width is larger - using its width
                    if int(self._font_chars[cnum][1]) > thewidth:
                        # gets the character real width (1)
                        thewidth = int(self._font_chars[cnum][1])
                else:
                    prevCorrectedLetter = False

                if valid and cnum != 0:  # if the index is 0, this is a space
                    # This is used to rotate symbols later
                    rotatingAngle = 0  # Prepare sin/cos for rotating the segments

                    if rotCheckbox_Checked:
                        rotatingAngle = random.randint(
                            self._minRotate, self._maxRotate - 1)
                    if differentSizeCheckbox_Checked:  # scaling by the modifier
                        scale = float(fontscale_value_Text) / 5
                        scale *= random.uniform(0, 1) * (
                            1 - self._symbolSizeRandomizer) + self._symbolSizeRandomizer

                    b = 0
                    # loop through the stroke x/y pairs     //Needed some extra iterations here
                    while b < math.trunc(len(self._font_chars[cnum]) / float(4)):

                        if float(self._font_chars[cnum][(b * 4) + 3 + 3]) >= 0 and float(self._font_chars[cnum][b * 4 + 3]) >= 0:

                            # the +3 is because there are 3 array elements prior to x/y pair data in the array.
                            x1 = float(self._font_chars[cnum][(b * 4) + 3])
                            y1 = float(self._font_chars[cnum][(b * 4) + 3 + 1])
                            x2 = float(self._font_chars[cnum][(b * 4) + 3 + 2])
                            y2 = float(self._font_chars[cnum][(b * 4) + 3 + 3])
                            if lineGoingDownCheckbox_Checked:
                                y1 += lineFactor * 161  # 161 - symbol height!
                                y2 += lineFactor * 161
                            if rotCheckbox_Checked:  # Rotating the line
                                points = self._rotate(
                                    x1, y1, thewidth / 2, math.trunc(161 / float(2)), rotatingAngle)
                                x1 = points[0]
                                y1 = points[1]
                                points = self._rotate(
                                    x2, y2, thewidth / 2, math.trunc(161 / float(2)), rotatingAngle)
                                x2 = points[0]
                                y2 = points[1]

                            # Increasing the size and adding random movement
                            x1 = x1 * scale + xFactor * thewidth * multX * scale
                            x2 = x2 * scale + xFactor * thewidth * multX * scale
                            y1 = y1 * scale + yFactor * 37 * multY * scale
                            y2 = y2 * scale + yFactor * 37 * multY * scale

                            draw_x1 = accum_x + x1 + offx  # calculate the scaled points for the picutrebox
                            draw_y1 = (offy + accum_y) + y1
                            draw_x2 = accum_x + x2 + offx
                            draw_y2 = (offy + accum_y) + y2

                            # start a pen stroke
                            GX = accum_x + x1 + offx  # calculate the GCode X value
                            # calculate the GCode Y value
                            GY = ((char_height - y1) + (max_y - offy) -
                                  accum_y) - font_offset_y

                            # test if the pen needs to raise for a travel
                            if lastx == accum_x + x1 + offx and lasty == (char_height - y1) + (max_y - offy):
                                output += "G1 X" + str(GX) + " Y" + str((GY)) + " F" + str(
                                    F_travel if first_move else F_draw) + "\r\n"  # write the move to the output string
                                first_move = False
                            else:

                                output += "G0 Z" + penup_Text + " F" + \
                                    str(F_zspeed) + \
                                    "\r\n"  # raise the pen - Pen up

                                output += "G0 X" + \
                                    str(GX) + " Y" + str(GY) + " F" + \
                                    str(F_travel) + "\r\n"  # move the pen

                                # put the pen down (unless dry run is on)
                                output += "G0 Z" + pendown_Text + \
                                    " F" + str(F_zspeed) + "\r\n"

                            if int(GX) > max_x or int(GX) < 0:
                                out_of_bounds = True  # check if we went out of bounds
                            if int(GY) > max_y or int(GY) < 0:
                                out_of_bounds = True

                            # end the pen stroke
                            # calculate the GCode X value
                            GX = (accum_x + x2 + offx)
                            # calculate the GCode Y value
                            GY = (((char_height - y2) + (max_y - offy)) -
                                  accum_y) - font_offset_y
                            # write the move to the output string
                            output += "G1 X" + \
                                str(GX) + " Y" + str(GY) + \
                                " F" + str(F_draw) + "\r\n"

                            # keep the last x/y so we can test it for pen up on next loop
                            lastx = accum_x + x2 + offx
                            lasty = (char_height - y2) + (max_y - offy)
                        # found an input point! If there is an output point of previous letter - i'd draw a line
                        elif float(self._font_chars[cnum][(b * 4) + 3 + 3]) < 0 and prevOutputPointX != -1 and prevOutputPointY != -1 and connectLettersCheckBox_Checked:
                            x1 = prevOutputPointX
                            y1 = prevOutputPointY
                            x2 = float(self._font_chars[cnum][(b * 4) + 3])
                            y2 = float(self._font_chars[cnum][(b * 4) + 3 + 1])
                            if rotCheckbox_Checked:  # Rotating the line
                                points = None
                                points = self._rotate(
                                    x2, y2, thewidth / 2, math.trunc(161 / float(2)), rotatingAngle)
                                x2 = points[0]
                                y2 = points[1]

                            # Increasing the size and adding random movement
                            x2 = x2 * scale + xFactor * thewidth * multX * scale
                            y2 = y2 * scale + yFactor * 37 * multY * scale

                            draw_x1 = x1 + offx  # calculate the scaled points for the picutrebox
                            draw_y1 = (offy) + y1 + accum_y
                            draw_x2 = accum_x + x2 + offx
                            draw_y2 = (offy + accum_y) + y2

                            # start a pen stroke
                            GX = x1 + offx  # calculate the GCode X value
                            # calculate the GCode Y value
                            GY = ((char_height - y1) + (max_y - offy) -
                                  accum_y) - font_offset_y

                            # test if the pen needs to raise for a travel
                            if lastx == accum_x + x1 + offx and lasty == (char_height - y1) + (max_y - offy):
                                # write the move to the output string
                                output += "G1 X" + \
                                    str(GX) + " Y" + str((GY)) + " F" + \
                                    (F_travel if first_move else F_draw) + "\r\n"
                                first_move = False
                            else:

                                output += "G0 Z" + penup_Text + " F" + \
                                    str(F_zspeed) + \
                                    "\r\n"  # raise the pen - Pen up

                                output += "G0 X" + \
                                    str(GX) + " Y" + str(GY) + " F" + \
                                    str(F_travel) + "\r\n"  # move the pen

                                # put the pen down (unless dry run is on)
                                output += "G0 Z" + pendown_Text + \
                                    " F" + str(F_zspeed) + "\r\n"

                            if int(GX) > max_x or int(GX) < 0:
                                out_of_bounds = True  # check if we went out of bounds
                            if int(GY) > max_y or int(GY) < 0:
                                out_of_bounds = True

                            # end the pen stroke
                            # calculate the GCode X value
                            GX = (accum_x + x2 + offx)
                            # calculate the GCode Y value
                            GY = (((char_height - y2) + (max_y - offy)) -
                                  accum_y) - font_offset_y
                            # write the move to the output string
                            output += "G1 X" + \
                                str(GX) + " Y" + str(GY) + \
                                " F" + str(F_draw) + "\r\n"

                            # keep the last x/y so we can test it for pen up on next loop
                            lastx = accum_x + x2 + offx
                            lasty = (char_height - y2) + (max_y - offy)

                        else:  # there's an output point. Saving it and will use if there is an input point
                            x2 = float(self._font_chars[cnum][(b * 4) + 3 + 2])
                            y2 = float(self._font_chars[cnum][(b * 4) + 3 + 3])
                            if rotCheckbox_Checked:  # Rotating the line
                                points = None
                                points = self._rotate(
                                    x2, y2, thewidth / 2, math.trunc(161 / float(2)), rotatingAngle)
                                x2 = points[0]
                                y2 = points[1]

                            # Increasing the size and adding random movement
                            x2 = x2 * scale + xFactor * thewidth * multX * scale + accum_x
                            y2 = y2 * scale + yFactor * 37 * multY * scale
                            ifOuputPointFound = True
                            prevOutputPointY = y2
                            prevOutputPointX = x2

                        b += 1
                    if not ifOuputPointFound:
                        prevOutputPointX = -1
                        prevOutputPointY = -1
                    if not correctedLetter:
                        # accumulated X value plus spacing
                        accum_x += (float(thewidth) * scale) + letter_spacing
                    correctedLetter = False
                else:
                    # accumulated X value (space) plus spacing
                    accum_x += float(thewidth) * scale + letter_spacing
                    prevOutputPointX = -1
                    prevOutputPointY = -1
                a += 1
            accum_x = 0  # CR                                                    //reset the accumulated X value
            # LF                            //increment the accumulated Y value plus spacing
            accum_y += char_height + line_spacing
            # end lines loop
        if symbolMovingError:
            print("Random symbol moving function error. Check if you entered correct coefficients and try again.", end='')
        # end of ploting moves

        output += "G0 Z" + penup_Text + " F" + \
            str(F_zspeed) + "\r\n"  # Raise the pen

        output += "" + "\r\n"  # end space

        # Remove line duplicates, enforce periods instead of comma's in decimal numbers caused by language preferences
        output_filtered = ""
        lastline = ""
        lines_omitted = 0

        lines = output.split("\r\n")
        for line in lines:
            line = line.strip()
            if line is not None:
                print(line)
                if line is not None and lastline != line:
                    output_filtered += line.replace(",", ".") + "\r\n"
                    lastline = line
                else:
                    if line is not None:
                        output_filtered += line.replace(",", ".") + "\r\n"
                    lines_omitted += 1

        # keep an eye on the duplicate lines for further refinement later
        output_filtered += "; lines omitted: " + str(lines_omitted) + "\r\n"
        print(output_filtered)

        if out_of_bounds:
            print("Out of Bounds")

    def _rotate(self, thisPointX, thisPointY, originPointX, originPointY, degrees):
        radians = (math.pi / 180) * degrees
        #x, y = thispoint
        #offset_x, offset_y = originpoint
        adjusted_x = (thisPointX - originPointX)
        adjusted_y = (thisPointY - originPointY)
        cos_rad = math.cos(radians)
        sin_rad = math.sin(radians)
        result = []
        result.append(originPointX + cos_rad *
                      adjusted_x + sin_rad * adjusted_y)
        result.append(originPointY + -sin_rad *
                      adjusted_x + cos_rad * adjusted_y)
        return result
