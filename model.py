import tensorflow as tf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# Path of saved model
save_file = '/home/soyoung/model/model_morning.ckpt'

class MODEL:
    def __init__(self, file_path):
        self.path = file_path

        # Neural Net Basic Models
        self.ph_color_image = tf.placeholder(tf.float32, [None, 112, 112, 3])
        self.ph_binary_image = tf.placeholder(tf.float32, [None, 112, 112, 3])

    def encoder(self, inputs):
        with tf.variable_scope('encoder', reuse=tf.AUTO_REUSE):
            en_conv1 = tf.layers.conv2d(inputs=inputs, filters=32, kernel_size=[5, 5],
                                        padding="SAME", activation=tf.nn.relu,
                                        kernel_initializer=tf.contrib.layers.xavier_initializer())
            en_pool1 = tf.layers.max_pooling2d(inputs=en_conv1, pool_size=[2, 2], padding="SAME", strides=2)

            en_conv2 = tf.layers.conv2d(inputs=en_pool1, filters=64, kernel_size=[3, 3],
                                        padding="SAME", activation=tf.nn.relu,
                                        kernel_initializer=tf.contrib.layers.xavier_initializer())
            en_pool2 = tf.layers.max_pooling2d(inputs=en_conv2, pool_size=[2, 2], padding="SAME", strides=2)

            en_conv3 = tf.layers.conv2d(inputs=en_pool2, filters=128, kernel_size=[3, 3],
                                        padding="SAME", activation=tf.nn.relu,
                                        kernel_initializer=tf.contrib.layers.xavier_initializer())
            en_pool3 = tf.layers.max_pooling2d(inputs=en_conv3, pool_size=[2, 2], padding="SAME", strides=2)

            en_conv4 = tf.layers.conv2d(inputs=en_pool3, filters=256, kernel_size=[3, 3],
                                        padding="SAME", activation=tf.nn.relu,
                                        kernel_initializer=tf.contrib.layers.xavier_initializer())
            en_pool4 = tf.layers.max_pooling2d(inputs=en_conv4, pool_size=[2, 2], padding="SAME", strides=2)

            flat = tf.reshape(en_pool4, [-1, 7 * 7 * 256])

            # output = tf.layers.dense(inputs=flat, units=1024, activation=None)

        return en_pool1, en_pool2, en_pool3, flat

    def generator(self, inputs, en_pool3, en_pool2, en_pool1):
        with tf.variable_scope('generator'):
            # g_dense = tf.reshape(inputs, [-1, 7*7*128])

            g_inputs = tf.reshape(inputs, [-1, 7, 7, 256])

            # 7 7 256
            g_conv1 = tf.layers.conv2d_transpose(inputs=g_inputs, filters=128, kernel_size=[3, 3],
                                                 padding="SAME", strides=2, activation=tf.nn.relu,
                                                 kernel_initializer=tf.contrib.layers.xavier_initializer())

            # 14 14 128
            g_conv1_concat = tf.concat([g_conv1, en_pool3], axis=3)
            g_conv2 = tf.layers.conv2d_transpose(inputs=g_conv1_concat, filters=64, kernel_size=[3, 3],
                                                 padding="SAME", strides=2, activation=tf.nn.relu,
                                                 kernel_initializer=tf.contrib.layers.xavier_initializer())

            # 28 28 64
            g_conv2_concat = tf.concat([g_conv2, en_pool2], axis=3)
            g_conv3 = tf.layers.conv2d_transpose(inputs=g_conv2_concat, filters=32, kernel_size=[3, 3],
                                                 padding="SAME", strides=2, activation=tf.nn.relu,
                                                 kernel_initializer=tf.contrib.layers.xavier_initializer())

            # 56 56 32
            g_conv3_concat = tf.concat([g_conv3, en_pool1], axis=3)
            g_conv4 = tf.layers.conv2d_transpose(inputs=g_conv3_concat, filters=3, kernel_size=[5, 5],
                                                 padding="SAME", strides=2, activation=tf.nn.tanh,
                                                 kernel_initializer=tf.contrib.layers.xavier_initializer())

            output = tf.reshape(g_conv4, [-1, 112, 112, 3])

        return output


    def Make(self):
        input_bi = Image.open(self.path)
        input_bi = input_bi.resize((112, 112))
        input_bi = np.array(input_bi)

        # Options
        total_epoch = 300
        batch_size = 64
        n_input = 112 * 112 * 3
        learning_rate = 0.0002

        en_pool1, en_pool2, en_pool3, flat = self.encoder(self.ph_binary_image)

        G_image = self.generator(flat, en_pool3, en_pool2, en_pool1)

        dif_image = tf.square(tf.subtract(G_image, self.ph_color_image))

        match_img_loss = tf.reduce_mean(
            tf.square(tf.subtract(tf.reduce_mean(G_image, axis=3), tf.reduce_mean(self.ph_binary_image, axis=3))))

        loss_G = 5 * tf.reduce_mean(dif_image) + match_img_loss

        vars_E = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES,
                                   scope='encoder')
        vars_G = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES,
                                   scope='generator')

        vars = vars_E + vars_G

        train = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(loss_G, var_list=vars)

        saver = tf.train.Saver()

        sess = tf.Session()
        sess.run(tf.global_variables_initializer())

        total_batch = int(3000 / batch_size)
        cost = 0

        saver.restore(sess, save_file)

        sample_size = 1
        input_bi_feed = np.asarray(input_bi).reshape((1, 112, 112, 3))
        samples = sess.run(G_image,
                           feed_dict={self.ph_binary_image: (input_bi_feed - 127.5) / 255.})

        bin_img = (input_bi / 255.)
        smp_img = ((samples[0] + 1.) / 2.)
        fig = plt.figure(1)
        plt.subplot(121)
        plt.title("Input Binary Image")
        plt.axis('off')
        plt.imshow(bin_img)
        
        plt.subplot(122)
        plt.title("Output RGB Image")
        plt.axis('off')
        plt.imshow(smp_img)
        
        print("################################333")

        plt.savefig('/home/soyoung/static/{}.png'.format(str('colorimage').zfill(3)), bbox_inches='tight')
        plt.close(fig)
        print('Colorization Finished!')

        return 'colorimage.png'

