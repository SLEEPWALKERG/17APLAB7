from threading import Thread

import wx
import random

SPEED = 300
selectDifficulty = 101

pause = ord('P')
left = wx.WXK_LEFT
right = wx.WXK_RIGHT
down = wx.WXK_DOWN
up = wx.WXK_UP
space = wx.WXK_SPACE
fast = ord('D')


def myasync(func):
    def wrapper(*args, **kwargs):
        thr = Thread(target=func, args=args, kwargs=kwargs)
        thr.start()
    return wrapper

class MyModeDlg(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "复选显示位图选择", size=(400, 300))
        panel = wx.Panel(self)
        wx.Button(panel, wx.ID_OK, "确定", size=(80, 30), pos=(200, 50)).SetDefault()
        wx.Button(panel, wx.ID_CANCEL, "取消", size=(80, 30), pos=(200, 150))
        self.p = wx.Button(panel, 801, "Pause:   " + chr(pause),size=(120,30),pos=(50,20))
        self.l = wx.Button(panel, 802, "Left:   " + chr(pause), size=(120, 30), pos=(50, 50))
        self.r = wx.Button(panel, 803, "Right:   " + chr(pause), size=(120, 30), pos=(50, 80))
        self.whirl_1 = wx.Button(panel, 804, "Whirl_1:   " + chr(pause), size=(120, 30), pos=(50, 110))
        self.whirl_2 = wx.Button(panel, 805, "Whirl_2:   " + chr(pause), size=(120, 30), pos=(50, 140))
        self.fall = wx.Button(panel, 806, "Fall:   " + chr(pause), size=(120, 30), pos=(50, 170))
        self.accelerate = wx.Button(panel, 807, "Accelerate:   " + chr(pause), size=(120, 30), pos=(50, 200))
        self.Bind(wx.EVT_BUTTON, self.Handle_Button)
        self.Bind(wx.EVT_KEY_DOWN, self.Handle_Key)

    def Handle_Button(self, evt):
        id = evt.GetId()
        if id == wx.ID_OK:
            self.GetParent().Refresh()
            self.Destroy()
        elif id == wx.ID_CANCEL:
            self.Destroy()
        elif id == 801:
            self.p.SetLabel("Pause:")

    @myasync
    def Handle_Key(self, event):
        keycode = event.GetKeyCode()
        print(keycode)




class Tetris(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(300, 600))

        '''self.icon = wx.Icon(name="icon.ico", type=wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)'''

        self.menuBar = wx.MenuBar()

        self.menu1 = wx.Menu()
        self.menu1.Append(501, "Key Binding(&k)\tF2")
        self.Bind(wx.EVT_MENU, self.onbinding, id=501)
        self.menu1.Append(502, "Restart(&R)\tAlt+R")
        self.Bind(wx.EVT_MENU, self.OnRestart, id=502)
        self.menu1.Append(503, "Time Used(Have to pause the game)")
        self.Bind(wx.EVT_MENU, self.OnCostTime, id=503)
        self.menu1.Append(wx.ID_EXIT, "Exit(&X)")
        self.Bind(wx.EVT_MENU, self.OnClose, id=wx.ID_EXIT)
        self.menuBar.Append(self.menu1, "File(&F)")
        self.menuBar.Enable(503, False)

        self.menu2 = wx.Menu()
        self.menu2.Append(101, "Easy\tCtrl+1", "", wx.ITEM_RADIO)
        self.menu2.Append(102, "Medium\tCtrl+2", "", wx.ITEM_RADIO)
        self.menu2.Append(103, "Difficult\tCtrl+3", "", wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU_RANGE, self.OnDifficulty, id=101, id2=103)
        self.menuBar.Append(self.menu2, "Difficulty(&D)")
        global selectDifficulty
        self.menuBar.Check(selectDifficulty, True)

        self.menu3 = wx.Menu()
        self.menu3.Append(301, "Information(&I)\tF1")
        self.Bind(wx.EVT_MENU, self.OnAbout, id=301)
        self.menuBar.Append(self.menu3, "About(&A)")

        self.SetMenuBar(self.menuBar)
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText('0')
        self.board = Board(self)
        self.board.SetFocus()
        self.board.start()
        self.Centre()
        self.Show(True)

    def onbinding(self, evt):
        if not self.board.isPaused:
            self.board.pause()
        MyModeDlg(self).ShowModal()
        self.board.pause()


    def OnDifficulty(self, evt):
        number = evt.GetId()
        global SPEED
        global selectDifficulty
        title = ""
        if number == 101:
            SPEED = 300
            selectDifficulty = 101
            title = "Tetris(Easy)"
        elif number == 102:
            SPEED = 200
            selectDifficulty = 102
            title = "Tetris(Medium)"
        else:
            SPEED = 100
            selectDifficulty = 103
            title = "Tetris(Difficult)"
        Tetris(None, title=title)
        self.Destroy()

    def OnRestart(self, evt):
        Tetris(None, title='Tetris')
        self.Destroy()

    def OnCostTime(self, evt):
        wx.MessageBox('You have played %.1f seconds' % (1.0 * self.board.costTime * self.board.Speed / 1000),
                      "Time Used", wx.OK | wx.ICON_INFORMATION, self)

    def OnAbout(self, evt):
        wx.MessageBox("17APLAB7(WX) Tetris",
                      "10160710417 顾铭", wx.OK | wx.ICON_INFORMATION, self)

    def OnClose(self, evt):
        self.Close()


class Board(wx.Panel):
    BoardWidth = 10
    BoardHeight = 22
    Speed = 300
    ID_TIMER = 1
    costTime = 0

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.WANTS_CHARS)
        global SPEED
        Board.Speed = SPEED

        self.initBoard()

    def initBoard(self):

        Board.costTime = 0
        self.timer = wx.Timer(self, Board.ID_TIMER)
        self.isWaitingAfterLine = False
        self.curPiece = Shape()
        self.nextPiece = Shape()
        self.curX = 0
        self.curY = 0
        self.numLinesRemoved = 0
        self.board = []
        self.isStarted = False
        self.isPaused = False
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_TIMER, self.OnTimer, id=Board.ID_TIMER)
        self.clearBoard()

    def shapeAt(self, x, y):

        return self.board[int((y * Board.BoardWidth) + x)]

    def setShapeAt(self, x, y, shape):

        self.board[int((y * Board.BoardWidth) + x)] = shape

    def squareWidth(self):

        return self.GetClientSize().GetWidth() / Board.BoardWidth

    def squareHeight(self):

        return self.GetClientSize().GetHeight() / Board.BoardHeight

    def start(self):

        if self.isPaused:
            return
        self.isStarted = True
        self.isWaitingAfterLine = False
        self.numLinesRemoved = 0
        self.clearBoard()
        self.newPiece()
        self.timer.Start(Board.Speed)

    def pause(self):

        if not self.isStarted:
            return
        self.isPaused = not self.isPaused
        statusbar = self.GetParent().statusbar

        if self.isPaused:
            self.GetParent().GetMenuBar().Enable(502, True)
        else:
            self.GetParent().GetMenuBar().Enable(502, False)

        if self.isPaused:
            self.timer.Stop()
            statusbar.SetStatusText('paused')
        else:
            self.timer.Start(Board.Speed)
            statusbar.SetStatusText(str(self.numLinesRemoved))
        self.Refresh()

    def clearBoard(self):

        for i in range(Board.BoardHeight * Board.BoardWidth):
            self.board.append(Tetrominoes.NoShape)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        size = self.GetClientSize()
        boardTop = size.GetHeight() - Board.BoardHeight * self.squareHeight()

        for i in range(Board.BoardHeight):
            for j in range(Board.BoardWidth):
                shape = self.shapeAt(j, Board.BoardHeight - i - 1)
                if shape != Tetrominoes.NoShape:
                    self.drawSquare(dc,
                                    0 + j * self.squareWidth(),
                                    boardTop + i * self.squareHeight(), shape)
        if self.curPiece.shape() != Tetrominoes.NoShape:
            for i in range(4):
                x = self.curX + self.curPiece.x(i)
                y = self.curY - self.curPiece.y(i)
                self.drawSquare(dc, 0 + x * self.squareWidth(),
                                boardTop + (Board.BoardHeight - y - 1) * self.squareHeight(),
                                self.curPiece.shape())

    def OnKeyDown(self, event):
        if not self.isStarted or self.curPiece.shape() == Tetrominoes.NoShape:
            event.Skip()
            return
        keycode = event.GetKeyCode()
        if keycode == pause:# or keycode == ord('p'):
            #print(keycode)
            self.pause()
            return
        if self.isPaused:
            return
        elif keycode == left:
            self.tryMove(self.curPiece, self.curX - 1, self.curY)
        elif keycode == right:
            self.tryMove(self.curPiece, self.curX + 1, self.curY)
        elif keycode == down:
            self.tryMove(self.curPiece.rotatedRight(), self.curX, self.curY)
        elif keycode == up:
            self.tryMove(self.curPiece.rotatedLeft(), self.curX, self.curY)
        elif keycode == space:
            self.dropDown()
        elif keycode == fast:
            self.oneLineDown()
        else:
            event.Skip()

    def OnTimer(self, event):

        if event.GetId() == Board.ID_TIMER:
            if self.isWaitingAfterLine:
                self.isWaitingAfterLine = False
                self.newPiece()
            else:
                self.oneLineDown()
        else:
            event.Skip()
        Board.costTime += 1

    def dropDown(self):

        newY = self.curY

        while newY > 0:
            if not self.tryMove(self.curPiece, self.curX, newY - 1):
                break
            newY -= 1
        self.pieceDropped()

    def oneLineDown(self):

        if not self.tryMove(self.curPiece, self.curX, self.curY - 1):
            self.pieceDropped()

    def pieceDropped(self):

        for i in range(4):
            x = self.curX + self.curPiece.x(i)
            y = self.curY - self.curPiece.y(i)
            self.setShapeAt(x, y, self.curPiece.shape())
        self.removeFullLines()
        if not self.isWaitingAfterLine:
            self.newPiece()

    def removeFullLines(self):

        numFullLines = 0
        statusbar = self.GetParent().statusbar
        rowsToRemove = []
        for i in range(Board.BoardHeight):
            n = 0
            for j in range(Board.BoardWidth):
                if not self.shapeAt(j, i) == Tetrominoes.NoShape:
                    n = n + 1
            if n == 10:
                rowsToRemove.append(i)
        rowsToRemove.reverse()
        for m in rowsToRemove:
            for k in range(m, Board.BoardHeight):
                for l in range(Board.BoardWidth):
                    self.setShapeAt(l, k, self.shapeAt(l, k + 1))
            numFullLines = numFullLines + len(rowsToRemove)
            if numFullLines > 0:
                self.numLinesRemoved = self.numLinesRemoved + numFullLines
                statusbar.SetStatusText(str(self.numLinesRemoved))
                self.isWaitingAfterLine = True
                self.curPiece.setShape(Tetrominoes.NoShape)
                self.Refresh()

    def newPiece(self):

        self.curPiece = self.nextPiece
        statusbar = self.GetParent().statusbar
        self.nextPiece.setRandomShape()
        self.curX = Board.BoardWidth / 2 + 1
        self.curY = Board.BoardHeight - 1 + self.curPiece.minY()
        if not self.tryMove(self.curPiece, self.curX, self.curY):
            self.curPiece.setShape(Tetrominoes.NoShape)
            self.timer.Stop()
            self.isStarted = False
            statusbar.SetStatusText('Game over')

    def tryMove(self, newPiece, newX, newY):

        for i in range(4):

            x = newX + newPiece.x(i)
            y = newY - newPiece.y(i)

            if x < 0 or x >= Board.BoardWidth or y < 0 or y >= Board.BoardHeight:
                return False
            if self.shapeAt(x, y) != Tetrominoes.NoShape:
                return False
        self.curPiece = newPiece
        self.curX = newX
        self.curY = newY
        self.Refresh()

        return True

    def drawSquare(self, dc, x, y, shape):

        colors = ['#000000', '#CC6666', '#66CC66', '#6666CC',
                  '#CCCC66', '#CC66CC', '#66CCCC', '#DAAA00']
        light = ['#000000', '#F89FAB', '#79FC79', '#7979FC',
                 '#FCFC79', '#FC79FC', '#79FCFC', '#FCC600']
        dark = ['#000000', '#803C3B', '#3B803B', '#3B3B80',
                '#80803B', '#803B80', '#3B8080', '#806200']
        pen = wx.Pen(light[shape])
        pen.SetCap(wx.CAP_PROJECTING)
        dc.SetPen(pen)
        dc.DrawLine(x, y + self.squareHeight() - 1, x, y)
        dc.DrawLine(x, y, x + self.squareWidth() - 1, y)
        darkpen = wx.Pen(dark[shape])
        darkpen.SetCap(wx.CAP_PROJECTING)
        dc.SetPen(darkpen)
        dc.DrawLine(x + 1, y + self.squareHeight() - 1,
                    x + self.squareWidth() - 1, y + self.squareHeight() - 1)
        dc.DrawLine(x + self.squareWidth() - 1,
                    y + self.squareHeight() - 1, x + self.squareWidth() - 1, y + 1)
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(colors[shape]))
        dc.DrawRectangle(x + 1, y + 1, self.squareWidth() - 2,
                         self.squareHeight() - 2)


class Tetrominoes(object):
    NoShape = 0
    ZShape = 1
    SShape = 2
    LineShape = 3
    TShape = 4
    SquareShape = 5
    LShape = 6
    MirroredLShape = 7


class Shape(object):
    coordsTable = (
        ((0, 0), (0, 0), (0, 0), (0, 0)),
        ((0, -1), (0, 0), (-1, 0), (-1, 1)),
        ((0, -1), (0, 0), (1, 0), (1, 1)),
        ((0, -1), (0, 0), (0, 1), (0, 2)),
        ((-1, 0), (0, 0), (1, 0), (0, 1)),
        ((0, 0), (1, 0), (0, 1), (1, 1)),
        ((-1, -1), (0, -1), (0, 0), (0, 1)),
        ((1, -1), (0, -1), (0, 0), (0, 1))
    )

    def __init__(self):

        self.coords = [[0, 0] for i in range(4)]
        self.pieceShape = Tetrominoes.NoShape
        self.setShape(Tetrominoes.NoShape)

    def shape(self):

        return self.pieceShape

    def setShape(self, shape):

        table = Shape.coordsTable[shape]
        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]
        self.pieceShape = shape

    def setRandomShape(self):

        self.setShape(random.randint(1, 7))

    def x(self, index):

        return self.coords[index][0]

    def y(self, index):

        return self.coords[index][1]

    def setX(self, index, x):

        self.coords[index][0] = x

    def setY(self, index, y):

        self.coords[index][1] = y

    def minX(self):

        m = self.coords[0][0]
        for i in range(4):
            m = min(m, self.coords[i][0])
        return m

    def maxX(self):

        m = self.coords[0][0]
        for i in range(4):
            m = max(m, self.coords[i][0])
        return m

    def minY(self):

        m = self.coords[0][1]
        for i in range(4):
            m = min(m, self.coords[i][1])
        return m

    def maxY(self):

        m = self.coords[0][1]

        for i in range(4):
            m = max(m, self.coords[i][1])
        return m

    def rotatedLeft(self):

        if self.pieceShape == Tetrominoes.SquareShape:
            return self
        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):
            result.setX(i, self.y(i))
            result.setY(i, -self.x(i))
        return result

    def rotatedRight(self):

        if self.pieceShape == Tetrominoes.SquareShape:
            return self
        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):
            result.setX(i, -self.y(i))
            result.setY(i, self.x(i))
        return result


if __name__ == '__main__':
    app = wx.App()
    Tetris(None, title='Tetris(Easy)')
    app.MainLoop()
