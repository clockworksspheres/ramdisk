import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import com.clockworksspheres.ramdisk

ApplicationWindow {
    id: root
    width: 520
    height: 480
    visible: true
    title: qsTr("Create Ramdisk")
    color: palette.window

    RamdiskController {
        id: controller
        size_mb: 512
        mount_point: ""
        selected_row: -1

        // Populate as soon as the QObject is ready
        Component.onCompleted: refreshList()
    }

    // Also refresh once the window is shown (covers late-ready QML bindings)
    Component.onCompleted: {
        controller.refreshList()
        // One more pass after the event loop settles
        delayedRefresh.start()
    }

    Timer {
        id: delayedRefresh
        interval: 150
        repeat: false
        onTriggered: controller.refreshList()
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 8

        Label {
            text: qsTr("Create Ramdisk")
            font.pixelSize: 18
            font.bold: true
            Layout.alignment: Qt.AlignHCenter
            color: palette.windowText
        }

        Label {
            text: qsTr("Ramdisk Size")
            color: palette.windowText
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Slider {
                id: sizeSlider
                Layout.fillWidth: true
                from: 1
                to: Math.max(controller.max_size_mb, 512)
                stepSize: 1
                value: controller.size_mb
                onMoved: controller.setSizeFromSlider(Math.round(value))
            }

            TextField {
                Layout.preferredWidth: 90
                text: controller.size_mb + "M"
                horizontalAlignment: TextInput.AlignHCenter
                onEditingFinished: {
                    var n = parseInt(text)
                    if (!isNaN(n) && n > 0) {
                        controller.size_mb = n
                        sizeSlider.value = n
                    }
                }
            }

            Button {
                text: qsTr("Create Ramdisk")
                highlighted: true
                onClicked: controller.createRamdisk()
            }
        }

        Label {
            text: qsTr("Ramdisk Mount Point")
            color: palette.windowText
        }

        TextField {
            Layout.fillWidth: true
            placeholderText: qsTr("leave empty for temporary path")
            text: controller.mount_point
            onTextChanged: controller.mount_point = text
            Keys.onReturnPressed: controller.createRamdisk()
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Button {
                text: qsTr("Eject Ramdisk")
                onClicked: controller.ejectSelected()
            }
            Button {
                text: qsTr("Refresh")
                onClicked: controller.refreshList()
            }
            Item { Layout.fillWidth: true }
            Button {
                text: qsTr("Quit")
                onClicked: Qt.quit()
            }
        }

        Frame {
            Layout.fillWidth: true
            Layout.fillHeight: true
            padding: 0

            ColumnLayout {
                anchors.fill: parent
                spacing: 0

                Rectangle {
                    Layout.fillWidth: true
                    height: 28
                    color: palette.mid
                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 8
                        anchors.rightMargin: 8
                        Label {
                            text: qsTr("Device")
                            font.bold: true
                            Layout.preferredWidth: parent.width * 0.4
                            color: palette.windowText
                        }
                        Label {
                            text: qsTr("Mount Point")
                            font.bold: true
                            Layout.fillWidth: true
                            color: palette.windowText
                        }
                    }
                }

                ListView {
                    id: table
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    // Re-bind when row_count changes
                    model: controller.row_count
                    currentIndex: controller.selected_row

                    highlight: Rectangle {
                        color: palette.highlight
                        opacity: 0.3
                    }

                    // Force re-evaluation of delegates when list text changes
                    property string _devKey: controller.device_list_text
                    property string _mntKey: controller.mount_list_text

                    delegate: ItemDelegate {
                        width: table.width
                        height: 32
                        required property int index

                        // Depend on the keys so cells update after refresh
                        readonly property string deviceText: {
                            var _ = table._devKey
                            return controller.deviceAt(index)
                        }
                        readonly property string mountText: {
                            var _ = table._mntKey
                            return controller.mountAt(index)
                        }

                        contentItem: RowLayout {
                            Label {
                                text: deviceText
                                Layout.preferredWidth: parent.width * 0.4
                                elide: Text.ElideRight
                                color: palette.windowText
                            }
                            Label {
                                text: mountText
                                Layout.fillWidth: true
                                elide: Text.ElideMiddle
                                color: palette.windowText
                            }
                        }

                        onClicked: {
                            table.currentIndex = index
                            controller.selected_row = index
                        }
                        onDoubleClicked: {
                            controller.selected_row = index
                            controller.status_message =
                                deviceText + " → " + mountText
                        }
                    }

                    ScrollBar.vertical: ScrollBar {}
                }
            }
        }

        Label {
            text: controller.status_message
            Layout.fillWidth: true
            elide: Text.ElideRight
            color: palette.windowText
            font.italic: true
        }
    }
}
