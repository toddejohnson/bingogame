#!/usr/bin/env python
import random
import wx
import wx.lib.buttons as buttons
import sys
import os
from gtts import gTTS
from pygame import mixer
 
class BingoPanel(wx.Panel):
  def __init__(self, parent, terms):
    wx.Panel.__init__(self, parent)
    self.terms = terms
    self.termInd = 0
    self.X = 5
    self.Y = 5
    mixer.init()
    self.layoutWidgets()
    self.onNextWord()
  
  def layoutWidgets(self):
    mainSizer = wx.BoxSizer(wx.VERTICAL)
    self.fgSizer = wx.FlexGridSizer(rows=self.Y, cols=self.X, vgap=5, hgap=5)
    btnSizer = wx.BoxSizer(wx.HORIZONTAL)
    font = wx.Font(22, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                    wx.FONTWEIGHT_BOLD)
    size = (100,100)

    random.shuffle(self.terms)
    
    self.buttons = []
    for y in range(0,self.Y):
      row=[]
      for x in range(0, self.X):
        btn=buttons.GenToggleButton(self, size=size)
        btn.SetLabel(self.terms[y*self.X+x])
        btn.SetFont(font)
        btn.Bind(wx.EVT_BUTTON, self.onToggle)
        row.append(btn)
        self.fgSizer.Add(btn)
      self.buttons.append(row)
    self.normalBtnColour = self.buttons[0][0].GetBackgroundColour()
    random.shuffle(self.terms)
    mainSizer.Add(self.fgSizer, 0, wx.ALL|wx.CENTER, 5)

    self.repeatWord = wx.Button(self, label="Repeat")
    self.repeatWord.Bind(wx.EVT_BUTTON, self.onRepeatWordEv)
    btnSizer.Add(self.repeatWord, 0, wx.ALL | wx.CENTER, 5)

    self.nextWord = wx.Button(self, label="Next Word")
    self.nextWord.Bind(wx.EVT_BUTTON, self.onNextWordEv)
    btnSizer.Add(self.nextWord, 0, wx.ALL | wx.CENTER, 5)

    startOverBtn = wx.Button(self, label="Restart")
    startOverBtn.Bind(wx.EVT_BUTTON, self.onRestart)
    btnSizer.Add(startOverBtn, 0, wx.ALL|wx.CENTER, 5)
    mainSizer.Add(btnSizer, 0, wx.CENTER)

    self.SetSizer(mainSizer)

  def onRepeatWordEv(self,event):
    self.play(self.tts(self.terms[self.termInd]))

  def onNextWordEv(self,event):
    self.onNextWord()

  def onNextWord(self):
    self.termInd = self.termInd+1
    if len(self.terms)<self.termInd+1:
      msg = "You lost. Would you like to play again?"
      dlg = wx.MessageDialog(None, msg, "Out of words!",
                             wx.YES_NO | wx.ICON_WARNING)
      result = dlg.ShowModal()
      if result == wx.ID_YES:
        wx.CallAfter(self.restart)
        dlg.Destroy()
        return
      else:
        return True
    self.play(self.tts(self.terms[self.termInd]))
  def play(self, file):
    mixer.music.load(file)
    mixer.music.play()

  def tts(self, word, ret=0):
    if ret > 3: 
      raise Exception("Error TTS word: " +word)
    
    name = word+".mp3"
    if not os.path.exists(name):
      tts = gTTS(word, 'en')
      tts.save(name)
    if os.stat(name).st_size <1:
      os.remove(name)
      self.tts(word,ret+1)
    return name

  def onRestart(self, event):
    self.restart()
 
  def onToggle(self, event):
    button = event.GetEventObject()
    if button.GetLabel() != self.terms[self.termInd]:
      button.SetValue(False)
    else:
      button.Disable()
      if not self.checkWin():
        self.onNextWord()

  def checkForWin(self):
    check_func = lambda arr: arr[0].GetToggle() == True and all(elem.GetToggle() for elem in arr)
    for row in self.buttons:
      if check_func(row):
        return row
    for col in [[row[i] for row in self.buttons] for i in range(self.X)]:
      if check_func(list(col)):
        return col

    fdiag=[self.buttons[idx][idx] for idx in range(self.X)]
    if check_func(fdiag):
      return fdiag
    rdiag=[self.buttons[idx][self.X-1-idx] for idx in range(self.X)]
    if check_func(rdiag):
      return rdiag
    
    return False

  def checkWin(self):
    win=self.checkForWin()
    if(win):
      for btn in win:
        btn.SetBackgroundColour("Yellow")
      self.Layout()
      msg = "You Won! Would you like to play again?"
      dlg = wx.MessageDialog(None, msg, "Winner!",
                              wx.YES_NO | wx.ICON_WARNING)
      result = dlg.ShowModal()
      if result == wx.ID_YES:
        wx.CallAfter(self.restart)
        dlg.Destroy()

  def restart(self):
    mixer.quit()
    random.shuffle(self.terms)
    for y in range(0, self.Y):
      for x in range(0, self.X):
        self.buttons[x][y].SetLabel(self.terms[y*self.X+x])
        self.buttons[x][y].SetValue(False)
        self.buttons[x][y].Enable()
        self.buttons[x][y].SetBackgroundColour(self.normalBtnColour)
    random.shuffle(self.terms)
    self.termInd = 0
    mixer.init()
    self.onNextWord()
 
class MainWindow(wx.Frame):
  def __init__(self, terms):
    title = "Bingo Card"
    wx.Frame.__init__(self, parent=None, title=title, size=(600,700))
    self.panel = BingoPanel(self, terms)
    self.Show()
 
if __name__ == "__main__":
  if len(sys.argv) > 1:
    file_name = sys.argv[1]
  else:
    file_name = 'words.txt'

  in_file = open(file_name, 'r')
  terms = [line.strip() for line in in_file.readlines()]
  terms = list(filter(lambda x: x != "", terms))
  in_file.close()

  app = wx.App(False)
  frame = MainWindow(terms)
  app.MainLoop()
