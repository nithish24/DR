from django.conf import settings
class integration:
    def integrate_automate(self,img_path):
        self.import_modules()
        self.define_variables(img_path)
        self.stage_1_model()
        self.inter_stage_check()
        return class_1,class_2

    def import_modules(self):
        global tf,cv2
        import tensorflow as tf
        import cv2

    def define_variables(self,img_path):
        Base_dir = str(settings.BASE_DIR.replace('\\','/'))
        self.Stage_1_model_location = Base_dir + '/static/models/New-Stage1Model-traindata.h5'
        self.Stage_2_model_location = Base_dir + '/static/models/New-Stage2Model.h5'
        self.image_location = img_path

    def reformat_class_val(self,arr):
        val = list(arr)
        self.predict = val.index(max(val))
        return self.predict

    def predict_class_val(self, model):
        img = cv2.imread(self.image_location,cv2.IMREAD_GRAYSCALE)
        img = img.reshape(1,256,256,1)
        out_arr = model.predict(img)
        return self.reformat_class_val(out_arr[0])

    def stage_1_model(self):
        self.model_stage_1 = tf.keras.models.load_model(self.Stage_1_model_location)
        global class_1 
        class_1  = self.predict_class_val(self.model_stage_1)
        print("Class predicted by Stage 1 Model : ", class_1)

    def inter_stage_check(self):
        if(class_1 == 1):
            self.stage_2_model()
        elif(class_1 == 0):
          return 0

    def stage_2_model(self):
        self.model_stage_2 = tf.keras.models.load_model(self.Stage_2_model_location)
        global class_2
        class_2  = self.predict_class_val(self.model_stage_2)
        print("Class predicted by Stage 2 Model : ", class_2)
        return (class_2)



i1 = integration()
del i1
