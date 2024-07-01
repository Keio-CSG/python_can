import can
import msg
import asyncio
import time


class HandleControllerCommand:
    def __init__(self):
        #self.bus = can.interface.Bus('ws://localhost:54701/', bustype='remote', preserve_timestamps=True)
        # self.bus = can.interface.Bus('test', bustype='virtual', preserve_timestamps=True)
        # PIXKITへの送信用
        self.bus = can.interface.Bus(bustype='socketcan', channel="can0", bitrate=500000, app_name='python-can')

        # CANメッセージを送信するかしないかを判断するFlag
        self.sendFlag = False

        # 非同期でCANを送る
        asyncio.new_event_loop().run_in_executor(None, self.canSend)
        
    
    def setHandleControllerCommandSend(self, steering, accel_pedal, brake_pedal):
        self.steering = steering
        self.accel_pedal = accel_pedal
        self.brake_pedal = brake_pedal
        self.convertHandleControllerParameterToCanBusParameter()
    
    # ハンドルコントロールが出力した値を、CANBUSに載せる値に変化する
    # 現状はただの int 変換のみ
    # ハンドルコントロールの使用に合わせて変更する
    def convertHandleControllerParameterToCanBusParameter(self):
        # マイナスの値は送れないので、+ 1しておく
        # 中心が 500 で、0~100になるようにしている
        self.canbus_steering = int((self.steering) * -500 + 500)
        self.canbus_accel_pedal = int(self.accel_pedal * 100)
        self.canbus_brake_pedal = int(self.brake_pedal * 100)
        self.message_Steering_Command = msg.Steering_Command()
        self.message_Steering_Command.setDataFromInt(1, 16, self.canbus_steering)
        self.message_Brake_Command = msg.Brake_Command()
        self.message_Brake_Command.setDataFromInt(1, 10, self.canbus_brake_pedal)
        self.message_Throttle_Command = msg.Throttle_Command()
        # jerk を 10 にするのがキモ
        if self.canbus_accel_pedal > 50:
            self.message_Throttle_Command.setDataFromInt(1, 0, 0, 38 * 256)
        else:
            self.message_Throttle_Command.setDataFromInt(1, 0, 0, 0)
        
        self.message_Steering_Command.toData()
        self.message_Brake_Command.toData()
        self.message_Throttle_Command.toData()

        # self.message_Throttle_Command.view()


        self.can_msg_Steering_Command = can.Message(arbitration_id = self.message_Steering_Command.msg_id, data= self.message_Steering_Command.data, is_extended_id = False)
        self.can_msg_Brake_Command = can.Message(arbitration_id = self.message_Brake_Command.msg_id, data= self.message_Brake_Command.data, is_extended_id = False)
        self.can_msg_Throttle_Command = can.Message(arbitration_id = self.message_Throttle_Command.msg_id, data= self.message_Throttle_Command.data, is_extended_id = False)
        
        self.can_msg_unknown= can.Message(arbitration_id=259,data=[1,4,0,0,0,0,0,0],is_extended_id =False)
        self.can_msg_unknown1= can.Message(arbitration_id=260,data=[0,0,0,0,0,0,0,0],is_extended_id =False)
        self.can_msg_unknown2= can.Message(arbitration_id=261,data=[0,1,0,0,0,0,0,0],is_extended_id =False)


    # レートをガン無視して送りまくっている
    def canSend(self):
        while True:
            if self.sendFlag:
                self.bus.send(self.can_msg_Steering_Command)
                self.bus.send(self.can_msg_Brake_Command)
                self.bus.send(self.can_msg_Throttle_Command)
                self.bus.send(self.can_msg_unknown)
                self.bus.send(self.can_msg_unknown1)
                self.bus.send(self.can_msg_unknown2)

                time.sleep(0.01)
    
    def startCanSend(self):
        self.sendFlag = True
    
    def stopCanSend(self):
        self.sendFlag = False

