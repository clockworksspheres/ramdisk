#include "CreateRamdiskWindow.hpp"
#include "ui_mainwindow.h"

#include "ramdisk/Utils.hpp"
#include "ramdisk/Logger.hpp"
#include "ramdisk/Process.hpp"

#include <QMessageBox>
#include <QHeaderView>
#include <QIntValidator>
#include <QApplication>
#include <QTableWidgetItem>
#include <QInputDialog>
#include <QLineEdit>

#ifdef __linux__
#  include <unistd.h>
#endif

CreateRamdiskWindow::CreateRamdiskWindow(QWidget* parent)
    : QMainWindow(parent)
    , ui_(new Ui::MainWindow)
{
    ui_->setupUi(this);

    const auto maxMb = static_cast<int>(std::min<std::uint64_t>(
        availableMemoryMb() > 64 ? availableMemoryMb() - 64 : 512,
        65536));
    ui_->sizeHorizontalSlider->setRange(1, std::max(maxMb, 512));
    ui_->sizeHorizontalSlider->setValue(512);
    ui_->sizeLineEdit->setText(QString::number(512));
    ui_->sizeLineEdit->setValidator(new QIntValidator(1, maxMb, this));

    setupTable();
    setupConnections();
    populateFromSystem();

    ui_->createPushButton->setDefault(true);
    ui_->mountLineEdit->setFocus();
    setStatus(QString("Ready — platform: %1 (%2 existing)")
                  .arg(QString::fromStdString(ramdisk::platformName()))
                  .arg(ui_->tableWidget->rowCount()));
}

CreateRamdiskWindow::~CreateRamdiskWindow() {
    delete ui_;
}

std::uint64_t CreateRamdiskWindow::availableMemoryMb() const {
    return ramdisk::freeMemoryMb();
}

void CreateRamdiskWindow::setupTable() {
    ui_->tableWidget->setColumnCount(2);
    ui_->tableWidget->setHorizontalHeaderLabels({tr("device"), tr("mount point")});
    ui_->tableWidget->setRowCount(0);
    auto* header = ui_->tableWidget->horizontalHeader();
    header->setSectionResizeMode(QHeaderView::Stretch);
    ui_->tableWidget->setSelectionMode(QAbstractItemView::SingleSelection);
    ui_->tableWidget->setSelectionBehavior(QAbstractItemView::SelectRows);
    ui_->tableWidget->setEditTriggers(QAbstractItemView::NoEditTriggers);
}

void CreateRamdiskWindow::setupConnections() {
    connect(ui_->createPushButton, &QPushButton::clicked,
            this, &CreateRamdiskWindow::onCreateClicked);
    connect(ui_->ejectPushButton, &QPushButton::clicked,
            this, &CreateRamdiskWindow::onEjectClicked);
    connect(ui_->refreshPushButton, &QPushButton::clicked,
            this, &CreateRamdiskWindow::onRefreshClicked);
    connect(ui_->quitPushButton, &QPushButton::clicked,
            this, &CreateRamdiskWindow::onQuitClicked);
    connect(ui_->actionAbout, &QAction::triggered,
            this, &CreateRamdiskWindow::onAboutTriggered);

    connect(ui_->sizeHorizontalSlider, &QSlider::valueChanged,
            this, &CreateRamdiskWindow::onSliderChanged);
    connect(ui_->sizeLineEdit, &QLineEdit::textChanged,
            this, &CreateRamdiskWindow::onSizeTextChanged);
    connect(ui_->mountLineEdit, &QLineEdit::returnPressed,
            this, &CreateRamdiskWindow::onCreateClicked);
    connect(ui_->tableWidget, &QTableWidget::doubleClicked,
            this, &CreateRamdiskWindow::onTableDoubleClicked);
}

void CreateRamdiskWindow::addRow(const QString& device, const QString& mountPoint) {
    // Avoid duplicates (same mount point)
    for (int r = 0; r < ui_->tableWidget->rowCount(); ++r) {
        auto* m = ui_->tableWidget->item(r, 1);
        if (m && m->text() == mountPoint) {
            auto* d = ui_->tableWidget->item(r, 0);
            if (d) d->setText(device);
            return;
        }
    }
    const int row = ui_->tableWidget->rowCount();
    ui_->tableWidget->insertRow(row);
    ui_->tableWidget->setItem(row, 0, new QTableWidgetItem(device));
    ui_->tableWidget->setItem(row, 1, new QTableWidgetItem(mountPoint));
}

void CreateRamdiskWindow::populateFromSystem() {
    ui_->tableWidget->setRowCount(0);
    try {
        const auto disks = ramdisk::listMountedRamDisks();
        for (const auto& d : disks) {
            addRow(QString::fromStdString(d.device),
                   QString::fromStdString(d.mountPoint));
        }
        setStatus(tr("Found %1 existing ramdisk(s)").arg(static_cast<int>(disks.size())));
    } catch (const std::exception& e) {
        setStatus(tr("Could not enumerate mounts: %1").arg(e.what()));
    }
}

void CreateRamdiskWindow::setStatus(const QString& msg) {
    ui_->statusLabel->setText(msg);
    statusBar()->showMessage(msg, 5000);
}

void CreateRamdiskWindow::onSliderChanged(int value) {
    if (updatingSize_) return;
    updatingSize_ = true;
    ui_->sizeLineEdit->setText(QString::number(value));
    updatingSize_ = false;
}

void CreateRamdiskWindow::onSizeTextChanged(const QString& text) {
    if (updatingSize_) return;
    bool ok = false;
    const int value = text.toInt(&ok);
    if (!ok) return;
    updatingSize_ = true;
    ui_->sizeHorizontalSlider->setValue(value);
    updatingSize_ = false;
}

bool CreateRamdiskWindow::ensureLinuxSudoPassword() {
#ifdef __linux__
    if (geteuid() == 0) {
        return true;  // already root
    }
    if (!linuxSudoPassword_.empty()) {
        return true;  // already prompted this session
    }
    bool ok = false;
    const QString pw = QInputDialog::getText(
        this,
        tr("Administrator privileges required"),
        tr("Creating or ejecting a ramdisk requires root.\n"
           "Enter your password for sudo:"),
        QLineEdit::Password,
        QString(),
        &ok);
    if (!ok || pw.isEmpty()) {
        setStatus(tr("Cancelled — sudo password required"));
        return false;
    }
    linuxSudoPassword_ = pw.toStdString();
    return true;
#else
    return true;
#endif
}

void CreateRamdiskWindow::onCreateClicked() {
    const auto sizeMb = static_cast<std::uint64_t>(ui_->sizeHorizontalSlider->value());
    if (sizeMb == 0) {
        QMessageBox::warning(this, tr("Invalid size"),
                             tr("Cannot create a ramdisk of size 0."));
        return;
    }

#ifdef __linux__
    if (!ensureLinuxSudoPassword()) {
        return;
    }
#endif

    ramdisk::RamDiskOptions opts;
    opts.sizeMb = sizeMb;
    opts.mountPoint = ui_->mountLineEdit->text().trimmed().toStdString();
#ifdef __linux__
    opts.sudoPassword = linuxSudoPassword_;
#endif

    setStatus(tr("Creating %1 MB ramdisk...").arg(sizeMb));
    QApplication::setOverrideCursor(Qt::WaitCursor);

    try {
        auto disk = ramdisk::createRamDisk(opts);
        QApplication::restoreOverrideCursor();

        if (!disk || !disk->success()) {
            // Wrong password? clear cache so next attempt re-prompts
#ifdef __linux__
            linuxSudoPassword_.clear();
#endif
            QMessageBox::critical(this, tr("Create failed"),
                                  tr("Failed to create ramdisk.\n"
                                     "Check the password and that sudo is allowed."));
            setStatus(tr("Create failed"));
            return;
        }

        auto [ok, mnt, dev] = disk->getData();
        // Leave mounted after the process exits / object is destroyed
        disk->releaseOwnership();
        ownedDisks_.push_back(std::move(disk));

        addRow(QString::fromStdString(dev), QString::fromStdString(mnt));
        setStatus(tr("Mounted %1 at %2")
                      .arg(QString::fromStdString(dev),
                           QString::fromStdString(mnt)));
    } catch (const std::exception& e) {
        QApplication::restoreOverrideCursor();
#ifdef __linux__
        linuxSudoPassword_.clear();
#endif
        QMessageBox::critical(this, tr("Error"),
                              QString::fromUtf8(e.what()));
        setStatus(tr("Error: %1").arg(e.what()));
    }
}

void CreateRamdiskWindow::onEjectClicked() {
    const auto selected = ui_->tableWidget->selectionModel()->selectedRows();
    if (selected.isEmpty()) {
        QMessageBox::information(this, tr("Eject"),
                                 tr("Select a row in the table first."));
        return;
    }

#ifdef __linux__
    if (!ensureLinuxSudoPassword()) {
        return;
    }
#endif

    // Remove from bottom to top so indices stay valid
    QList<int> rows;
    for (const auto& idx : selected) {
        rows.append(idx.row());
    }
    std::sort(rows.begin(), rows.end(), std::greater<int>());

    for (int row : rows) {
        auto* devItem = ui_->tableWidget->item(row, 0);
        auto* mntItem = ui_->tableWidget->item(row, 1);
        if (!devItem) continue;

        const QString device = devItem->text();
        const QString mount  = mntItem ? mntItem->text() : QString();

        // Prefer device; on Linux tmpfs the "device" may be "tmpfs" — use mount point
        QString target = device;
#if defined(__linux__)
        if (device == QLatin1String("tmpfs") || device.isEmpty()) {
            target = mount;
        }
#endif
        setStatus(tr("Unmounting %1...").arg(target));

        bool ok = false;
#ifdef __linux__
        if (geteuid() != 0 && !linuxSudoPassword_.empty()) {
            auto res = ramdisk::runShellSudo(
                "umount '" + target.toStdString() + "'", linuxSudoPassword_);
            if (!res.ok()) {
                res = ramdisk::runShellSudo(
                    "umount -l '" + target.toStdString() + "'", linuxSudoPassword_);
            }
            ok = res.ok();
            if (!ok && !mount.isEmpty() && mount != target) {
                res = ramdisk::runShellSudo(
                    "umount '" + mount.toStdString() + "'", linuxSudoPassword_);
                ok = res.ok();
            }
            if (!ok) {
                linuxSudoPassword_.clear();
            }
        } else {
            ok = ramdisk::umount(target.toStdString());
            if (!ok && !mount.isEmpty() && mount != target) {
                ok = ramdisk::umount(mount.toStdString());
            }
        }
#else
        ok = ramdisk::umount(target.toStdString());
        if (!ok && !mount.isEmpty() && mount != target) {
            ok = ramdisk::umount(mount.toStdString());
        }
#endif
        if (ok) {
            ui_->tableWidget->removeRow(row);
            setStatus(tr("Unmounted %1").arg(target));
        } else {
            QMessageBox::warning(this, tr("Eject failed"),
                                 tr("Could not unmount %1.").arg(target));
            setStatus(tr("Eject failed: %1").arg(target));
        }
    }
}

void CreateRamdiskWindow::onRefreshClicked() {
    populateFromSystem();
}

void CreateRamdiskWindow::onQuitClicked() {
    close();
}

void CreateRamdiskWindow::onAboutTriggered() {
    QMessageBox::about(this, tr("About Ramdisk"),
        tr("<h3>Ramdisk</h3>"
           "<p>Cross-platform RAM disk manager (C++ / Qt 6 port).</p>"
           "<p>Based on the Python project "
           "<a href=\"https://github.com/clockworksspheres/ramdisk\">"
           "clockworksspheres/ramdisk</a>.</p>"
           "<p>Library version logic matches the CLI tools in this tree.</p>"));
}

void CreateRamdiskWindow::onTableDoubleClicked(const QModelIndex& index) {
    if (!index.isValid()) return;
    const int row = index.row();
    auto* devItem = ui_->tableWidget->item(row, 0);
    auto* mntItem = ui_->tableWidget->item(row, 1);
    const QString msg = tr("Device: %1\nMount point: %2")
                            .arg(devItem ? devItem->text() : QString("-"),
                                 mntItem ? mntItem->text() : QString("-"));
    QMessageBox::information(this, tr("Mount info"), msg);
}

void CreateRamdiskWindow::closeEvent(QCloseEvent* event) {
    const auto reply = QMessageBox::question(
        this, tr("Quit"),
        tr("Are you sure you want to quit?\n\n"
           "Ramdisks left mounted will remain until you eject them."),
        QMessageBox::Yes | QMessageBox::No,
        QMessageBox::Yes);
    if (reply == QMessageBox::Yes) {
        event->accept();
    } else {
        event->ignore();
    }
}
