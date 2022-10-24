from .utils import *


class Sign(VFrame):
    signSignal = Signal(Json)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setMinimumWidth(250)

        lay = self.layout()

        signing_label = Label("Signing :", name="signing")
        lay.addWidget(signing_label)

        self.unique_id = LabeledLineEdit(
            label="Unique ID", required=True, placeholder="Enter Unique ID"
        )
        lay.addWidget(self.unique_id)

        self.password = LabeledLineEdit(
            label="Password", required=True, placeholder="Enter Password"
        )
        lay.addWidget(self.password)

        hlay = QHBoxLayout()
        lay.addLayout(hlay)

        hlay.addStretch()

        sign_in = TextButton("Sign In")
        sign_in.clicked.connect(self.sign_in)
        hlay.addWidget(sign_in)

        sign_up = LinkButton("Sign Up")
        sign_up.clicked.connect(self.sign_up)
        hlay.addWidget(sign_up)

        hlay.addStretch()

        self.signSignal.connect(self.sign_response)

    def check_input(self):
        inputs: list[str] = []
        if unique_id := self.unique_id.text():
            inputs.append(unique_id)
        if password := self.password.text():
            inputs.append(password)

        if len(inputs) == 2:
            return inputs
        else:
            QMessageBox.warning(
                self, "Invalid Inputs", "Both Unique ID and Password are required!"
            )

    @property
    def client(self):
        return AmeboUserClient.get_client()

    def sign_in(self):
        if inputs := self.check_input():
            unique_id, password = inputs
            self.client.signin(unique_id=unique_id, password=password)

    def sign_up(self):
        if inputs := self.check_input():
            unique_id, password = inputs
            self.client.signup(unique_id=unique_id, password=password)

    def sign_response(self, json: Json):
        action = json.action
        response = json.response

        if action == "signin":
            if response == 200:
                QMessageBox.information(
                    self,
                    "Sign In Successful",
                    f"ID = {json.id}, ONLINE = {json.status}.",
                )
                self.window().signin_successful()

            elif response == 400:
                QMessageBox.warning(
                    self, "Invalid Credentials", "Invalid Unique ID and / or Password."
                )

            elif response == 401:
                QMessageBox.critical(
                    self, "Simulatenous Sign In", f"Unique ID already logged in."
                )

        elif action == "signup":
            if response == 200:
                QMessageBox.information(self, "Sign Up Successful", f"ID = {json.id}.")

            elif response == 400:
                QMessageBox.warning(
                    self, "Invalid Credentials", "Invalid Unique ID and / or Password."
                )

            elif response == 401:
                QMessageBox.critical(
                    self,
                    "Invalid Credentials",
                    f'Invalid Unique ID "{self.check_input()[0]}" already exists.',
                )

    def sign_receiver(self, json: Json):
        self.signSignal.emit(json)

    def showEvent(self, event: PySide6.QtGui.QShowEvent) -> None:
        self.unique_id.setText("apata")
        self.password.setText("miracle")
        self.setMaximumHeight(self.height())

        self.client.add_receiver("signin", self.sign_receiver)
        self.client.add_receiver("signup", self.sign_receiver)

    def closeEvent(self, event: PySide6.QtGui.QCloseEvent) -> None:
        self.client.remove_receiver("signin", self.sign_receiver)
        self.client.remove_receiver("signup", self.sign_receiver)
