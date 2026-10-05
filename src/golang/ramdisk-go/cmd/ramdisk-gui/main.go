//go:build qt

// ramdisk-gui – Qt 6 desktop UI for ramdisk-go (MIQT v0.14 API).
//
// On Linux, Create and Eject each open a Local Authentication dialog
// (same layout/algorithm as Python local_auth.ui / local_auth_widget.py):
// collect password → sudo -S for the privileged mount/umount.
package main

import (
	"fmt"
	"os"
	"os/user"
	"runtime"
	"strconv"
	"strings"
	"time"

	"github.com/clockworksspheres/ramdisk-go"
	qt "github.com/mappu/miqt/qt6"
)

const defaultSizeMB = 512

func main() {
	if runtime.GOOS == "linux" {
		if os.Getenv("WAYLAND_DISPLAY") != "" || os.Getenv("XDG_SESSION_TYPE") == "wayland" {
			_ = os.Setenv("QT_QPA_PLATFORM", "xcb")
		}
	}

	qt.NewQApplication(os.Args)
	if isNight() {
		setDarkPalette()
	}

	w := newMainWindow()
	w.Show()
	qt.QApplication_Exec()
}

func isNight() bool {
	h := time.Now().Hour()
	return h >= 18 || h < 6
}

func setDarkPalette() {
	p := qt.NewQPalette()
	p.SetColor2(qt.QPalette__Window, qt.NewQColor3(53, 53, 53))
	p.SetColor2(qt.QPalette__WindowText, qt.NewQColor3(255, 255, 255))
	p.SetColor2(qt.QPalette__Base, qt.NewQColor3(42, 42, 42))
	p.SetColor2(qt.QPalette__Text, qt.NewQColor3(255, 255, 255))
	p.SetColor2(qt.QPalette__Button, qt.NewQColor3(53, 53, 53))
	p.SetColor2(qt.QPalette__ButtonText, qt.NewQColor3(255, 255, 255))
	p.SetColor2(qt.QPalette__Highlight, qt.NewQColor3(42, 130, 218))
	qt.QApplication_SetPalette(p)
}

// ---------------------------------------------------------------------------
// Local Authentication dialog — mirrors Python local_auth.ui / local_auth_widget
// ---------------------------------------------------------------------------

type localAuthDialog struct {
	*qt.QDialog
	userEdit *qt.QLineEdit
	passEdit *qt.QLineEdit
	accepted bool
	password string
	username string
}

// newLocalAuthDialog builds the same controls as Python local_auth.ui:
// title "Local Authentication", Username (read-only), Password (echo mode),
// OK / Cancel. Shown on every Linux create and eject.
func newLocalAuthDialog(parent *qt.QWidget) *localAuthDialog {
	d := &localAuthDialog{QDialog: qt.NewQDialog(parent)}
	d.SetWindowTitle("Local Authentication")
	d.Resize(337, 206)

	layout := qt.NewQVBoxLayout(d.QWidget)

	title := qt.NewQLabel3("Local Authentication")
	f := title.Font()
	f.SetBold(true)
	title.SetFont(f)
	layout.AddWidget(title.QWidget)

	layout.AddWidget(qt.NewQLabel3("Username").QWidget)
	d.userEdit = qt.NewQLineEdit2()
	if u, err := user.Current(); err == nil {
		d.userEdit.SetText(u.Username)
	}
	d.userEdit.SetReadOnly(true)
	layout.AddWidget(d.userEdit.QWidget)

	layout.AddWidget(qt.NewQLabel3("Password").QWidget)
	d.passEdit = qt.NewQLineEdit2()
	d.passEdit.SetEchoMode(qt.QLineEdit__Password)
	layout.AddWidget(d.passEdit.QWidget)

	buttons := qt.NewQDialogButtonBox2()
	buttons.SetStandardButtons(qt.QDialogButtonBox__Ok | qt.QDialogButtonBox__Cancel)
	layout.AddWidget(buttons.QWidget)

	buttons.OnAccepted(func() {
		d.username = strings.TrimSpace(d.userEdit.Text())
		d.password = d.passEdit.Text()
		d.accepted = true
		d.Accept()
	})
	buttons.OnRejected(func() {
		d.accepted = false
		d.password = ""
		d.Reject()
	})

	d.passEdit.SetFocus()
	return d
}

// promptLinuxAuth opens Local Authentication. Returns (password, true) on OK
// with a non-empty password, otherwise ("", false). No-op on non-Linux.
func promptLinuxAuth(parent *qt.QWidget) (string, bool) {
	if runtime.GOOS != "linux" {
		return "", true // non-Linux: no elevation needed for typical flows
	}
	if os.Geteuid() == 0 {
		return "", true // already root
	}
	dlg := newLocalAuthDialog(parent)
	dlg.Exec()
	if !dlg.accepted || strings.TrimSpace(dlg.password) == "" {
		return "", false
	}
	return dlg.password, true
}

// ---------------------------------------------------------------------------
// Main window
// ---------------------------------------------------------------------------

type mainWindow struct {
	*qt.QMainWindow

	sizeSlider *qt.QSlider
	sizeEdit   *qt.QLineEdit
	mountEdit  *qt.QLineEdit
	createBtn  *qt.QPushButton
	ejectBtn   *qt.QPushButton
	refreshBtn *qt.QPushButton
	quitBtn    *qt.QPushButton
	table      *qt.QTableWidget
	statusBar  *qt.QStatusBar
}

func newMainWindow() *mainWindow {
	w := &mainWindow{QMainWindow: qt.NewQMainWindow2()}
	w.SetWindowTitle("Create Ramdisk")
	w.Resize(520, 460)

	central := qt.NewQWidget2()
	w.SetCentralWidget(central)
	grid := qt.NewQGridLayout(central)

	title := qt.NewQLabel3("Create Ramdisk")
	f := title.Font()
	f.SetPointSize(f.PointSize() + 2)
	f.SetBold(true)
	title.SetFont(f)
	grid.AddWidget3(title.QWidget, 0, 0, 1, 4)

	grid.AddWidget2(qt.NewQLabel3("Ramdisk Size (MiB)").QWidget, 1, 0)

	maxMB := estimateMaxMB()
	w.sizeSlider = qt.NewQSlider2()
	w.sizeSlider.SetOrientation(qt.Horizontal)
	w.sizeSlider.SetMinimum(1)
	w.sizeSlider.SetMaximum(int(maxMB))
	w.sizeSlider.SetValue(defaultSizeMB)
	grid.AddWidget2(w.sizeSlider.QWidget, 2, 0)

	w.sizeEdit = qt.NewQLineEdit2()
	w.sizeEdit.SetText(strconv.Itoa(defaultSizeMB))
	w.sizeEdit.SetMaximumWidth(100)
	iv := qt.NewQIntValidator2(1, int(maxMB))
	w.sizeEdit.SetValidator(iv.QValidator)
	grid.AddWidget3(w.sizeEdit.QWidget, 2, 1, 1, 2)

	w.createBtn = qt.NewQPushButton3("Create Ramdisk")
	w.createBtn.SetDefault(true)
	grid.AddWidget2(w.createBtn.QWidget, 2, 3)

	grid.AddWidget3(qt.NewQLabel3("Ramdisk Mount Point (optional)").QWidget, 3, 0, 1, 4)

	w.mountEdit = qt.NewQLineEdit2()
	w.mountEdit.SetPlaceholderText("leave empty for automatic path")
	grid.AddWidget3(w.mountEdit.QWidget, 4, 0, 1, 4)

	w.ejectBtn = qt.NewQPushButton3("Eject Ramdisk")
	grid.AddWidget2(w.ejectBtn.QWidget, 5, 0)

	w.refreshBtn = qt.NewQPushButton3("Refresh")
	grid.AddWidget3(w.refreshBtn.QWidget, 5, 1, 1, 2)

	w.quitBtn = qt.NewQPushButton3("Quit")
	grid.AddWidget2(w.quitBtn.QWidget, 5, 3)

	w.table = qt.NewQTableWidget3(0, 2)
	w.table.SetHorizontalHeaderLabels([]string{"device", "mount point"})
	w.table.HorizontalHeader().SetSectionResizeMode(qt.QHeaderView__Stretch)
	w.table.SetSelectionBehavior(qt.QAbstractItemView__SelectRows)
	w.table.SetSelectionMode(qt.QAbstractItemView__SingleSelection)
	w.table.SetEditTriggers(qt.QAbstractItemView__NoEditTriggers)
	grid.AddWidget3(w.table.QWidget, 6, 0, 1, 4)

	w.statusBar = qt.NewQStatusBar2()
	w.SetStatusBar(w.statusBar)
	w.statusBar.ShowMessage("Ready")

	mb := w.MenuBar()
	helpMenu := mb.AddMenuWithTitle("Help")
	aboutAct := helpMenu.QWidget.AddActionWithText("About")
	aboutAct.OnTriggered(func() {
		qt.QMessageBox_About(w.QWidget,
			"About ramdisk-go",
			"ramdisk-go\n\nCross-platform ramdisk tool\nGo port of clockworksspheres/ramdisk\nQt 6 UI (MIQT)\n\n"+
				runtime.GOOS+"/"+runtime.GOARCH+" · "+runtime.Version())
	})

	w.wireSignals()
	w.refreshTable()
	return w
}

func (w *mainWindow) wireSignals() {
	w.sizeSlider.OnValueChanged(func(v int) {
		w.sizeEdit.SetText(strconv.Itoa(v))
	})
	w.sizeEdit.OnTextChanged(func(t string) {
		v, err := strconv.Atoi(strings.TrimSpace(t))
		if err != nil {
			return
		}
		if v < w.sizeSlider.Minimum() {
			v = w.sizeSlider.Minimum()
		}
		if v > w.sizeSlider.Maximum() {
			v = w.sizeSlider.Maximum()
		}
		if w.sizeSlider.Value() != v {
			w.sizeSlider.SetValue(v)
		}
	})

	w.createBtn.OnClicked(func() { w.onCreate() })
	w.ejectBtn.OnClicked(func() { w.onEject() })
	w.refreshBtn.OnClicked(func() { w.refreshTable() })
	w.quitBtn.OnClicked(func() { w.Close() })
	w.mountEdit.OnReturnPressed(func() { w.onCreate() })
	w.table.OnDoubleClicked(func(*qt.QModelIndex) { w.onShowRow() })
}

func (w *mainWindow) onCreate() {
	sizeStr := strings.TrimSpace(w.sizeEdit.Text())
	size, err := strconv.ParseUint(sizeStr, 10, 64)
	if err != nil || size == 0 {
		qt.QMessageBox_Warning(w.QWidget, "Invalid size",
			"Enter a size in MiB greater than 0.")
		return
	}

	// Linux: same algorithm as Python createRamdisk() — prompt every time
	passwd, ok := promptLinuxAuth(w.QWidget)
	if !ok {
		w.statusBar.ShowMessage2("Authentication cancelled", 3000)
		return
	}

	opts := ramdisk.Options{SizeMB: size, LinuxSudoPassword: passwd}
	mp := strings.TrimSpace(w.mountEdit.Text())
	if mp != "" && mp != "put mountpoint here" {
		opts.MountPoint = mp
	}

	w.statusBar.ShowMessage("Creating ramdisk…")
	qt.QCoreApplication_ProcessEvents()

	rd, err := ramdisk.New(opts)
	if err != nil {
		qt.QMessageBox_Critical(w.QWidget, "Create failed", err.Error())
		w.statusBar.ShowMessage2("Create failed", 5000)
		return
	}

	info := rd.GetData()
	_ = rd.Detach()

	// Add the new row immediately so the user can select/eject it
	// even if ListMounted is slow or filters the path.
	w.addRow(info.Device, info.MountPoint)

	w.statusBar.ShowMessage2(fmt.Sprintf("Mounted at %s", info.MountPoint), 8000)
	w.mountEdit.SetText("")
	// Full refresh keeps table in sync with the system
	w.refreshTable()

	qt.QMessageBox_Information(w.QWidget, "Ramdisk created",
		fmt.Sprintf("success = %v\nmount   = %s\ndevice  = %s",
			info.Success, info.MountPoint, info.Device))
}

// addRow inserts one device/mount-point pair if that mount path is not already listed.
func (w *mainWindow) addRow(device, mountPoint string) {
	if mountPoint == "" {
		return
	}
	for r := 0; r < w.table.RowCount(); r++ {
		if it := w.table.Item(r, 1); it != nil && it.Text() == mountPoint {
			return // already present
		}
	}
	row := w.table.RowCount()
	w.table.InsertRow(row)
	w.table.SetItem(row, 0, qt.NewQTableWidgetItem2(device))
	w.table.SetItem(row, 1, qt.NewQTableWidgetItem2(mountPoint))
	w.table.SelectRow(row)
}

func (w *mainWindow) onEject() {
	row := w.table.CurrentRow()
	if row < 0 {
		qt.QMessageBox_Warning(w.QWidget, "No selection",
			"Select a ramdisk row in the table first.")
		return
	}
	devItem := w.table.Item(row, 0)
	mpItem := w.table.Item(row, 1)
	target := ""
	if mpItem != nil && mpItem.Text() != "" {
		target = mpItem.Text()
	} else if devItem != nil {
		target = devItem.Text()
	}
	if target == "" {
		qt.QMessageBox_Warning(w.QWidget, "Empty row",
			"Selected row has no mount path or device.")
		return
	}

	// Linux: prompt for every eject (Python remove() + _LocalAuth)
	passwd, ok := promptLinuxAuth(w.QWidget)
	if !ok {
		w.statusBar.ShowMessage2("Authentication cancelled", 3000)
		return
	}

	w.statusBar.ShowMessage("Ejecting " + target + "…")
	qt.QCoreApplication_ProcessEvents()

	var err error
	if runtime.GOOS == "linux" && passwd != "" {
		err = ramdisk.UmountPathWithPassword(target, passwd)
	} else {
		err = ramdisk.UmountPath(target)
	}
	if err != nil {
		qt.QMessageBox_Critical(w.QWidget, "Eject failed", err.Error())
		w.statusBar.ShowMessage2("Eject failed", 5000)
		return
	}
	w.statusBar.ShowMessage2("Ejected "+target, 5000)
	w.refreshTable()
}

func (w *mainWindow) onShowRow() {
	row := w.table.CurrentRow()
	if row < 0 {
		return
	}
	dev, mp := "", ""
	if it := w.table.Item(row, 0); it != nil {
		dev = it.Text()
	}
	if it := w.table.Item(row, 1); it != nil {
		mp = it.Text()
	}
	qt.QMessageBox_Information(w.QWidget, "Ramdisk",
		fmt.Sprintf("device:  %s\nmount:   %s", dev, mp))
}

func (w *mainWindow) refreshTable() {
	w.table.SetRowCount(0)
	list, err := ramdisk.ListMounted()
	if err != nil {
		w.statusBar.ShowMessage2("List error: "+err.Error(), 5000)
		return
	}
	for i, m := range list {
		w.table.InsertRow(i)
		w.table.SetItem(i, 0, qt.NewQTableWidgetItem2(m.Device))
		w.table.SetItem(i, 1, qt.NewQTableWidgetItem2(m.MountPoint))
	}
	w.statusBar.ShowMessage2(fmt.Sprintf("%d ramdisk(s)", len(list)), 3000)
}

func estimateMaxMB() uint64 {
	data, err := os.ReadFile("/proc/meminfo")
	if err == nil {
		for _, line := range strings.Split(string(data), "\n") {
			if strings.HasPrefix(line, "MemAvailable:") {
				fields := strings.Fields(line)
				if len(fields) >= 2 {
					kb, _ := strconv.ParseUint(fields[1], 10, 64)
					mb := kb / 1024
					if mb > 64 {
						return mb - 64
					}
					return mb
				}
			}
		}
	}
	return 8192
}
