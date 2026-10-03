#pragma once

#include <QMainWindow>
#include <QCloseEvent>
#include <memory>
#include <vector>
#include "ramdisk/RamDisk.hpp"

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class CreateRamdiskWindow : public QMainWindow {
    Q_OBJECT

public:
    explicit CreateRamdiskWindow(QWidget* parent = nullptr);
    ~CreateRamdiskWindow() override;

protected:
    void closeEvent(QCloseEvent* event) override;

private slots:
    void onCreateClicked();
    void onEjectClicked();
    void onRefreshClicked();
    void onQuitClicked();
    void onAboutTriggered();
    void onSliderChanged(int value);
    void onSizeTextChanged(const QString& text);
    void onTableDoubleClicked(const QModelIndex& index);

private:
    void setupConnections();
    void setupTable();
    void addRow(const QString& device, const QString& mountPoint);
    void setStatus(const QString& msg);
    std::uint64_t availableMemoryMb() const;

    Ui::MainWindow* ui_ = nullptr;
    bool updatingSize_ = false;

    // Keep ownership of disks created without --release so we can track them;
    // we call releaseOwnership() so they survive if the user wants them to.
    std::vector<std::unique_ptr<ramdisk::IRamDisk>> ownedDisks_;
};
