import numpy as np
from math import ceil

byte_depth_to_dtype = {1: np.uint8, 2: np.uint16, 4: np.uint32, 8: np.uint64}


def roundup(x, base=1):
    return int(ceil(x / base)) * base


# 为音频添加隐写内容
def lsb_interleave_bytes(carrier, payload, num_lsb, max_bytes_to_hide, truncate=False, byte_depth=1):
    # 将隐写内容进行二进制转换
    plen = len(payload)
    payload_bits = np.zeros(shape=(roundup(plen, num_lsb), 8), dtype=np.uint8)
    # [:plen, :]取0-plen行的所有列，unpackbits转换成二进制
    payload_bits[:plen, :] = np.unpackbits(
        # frombuffer将data以流的形式读入转化成ndarray对象
        # 第一个参数为stream,第二个参数为返回值的数据类型，第三个参数指定从stream的第几位开始读入
        np.frombuffer(payload, dtype=np.uint8, count=plen)
        # 将数据转换成plen行，8列进行展示
    ).reshape(plen, 8)

    # 设置范围数增强鲁棒性
    scope_num = set_scope_num(max_bytes_to_hide)
    count = int(max_bytes_to_hide) / scope_num
    print("add steg count:" + str(count))
    for i in range(int(count)):
        # 获取隐写内容的最大值
        bit_height = roundup(np.size(payload_bits) / num_lsb)
        carrier_dtype = byte_depth_to_dtype[byte_depth]
        # 对源数据进行二进制转换（仅转换需要替换最低有效位的数据）
        carrier_bits = np.unpackbits(
            np.frombuffer(carrier, dtype=carrier_dtype, count=bit_height + i * scope_num).view(
                np.uint8
            )
        ).reshape(bit_height + i * scope_num, 8 * byte_depth)
        # 替换原音频内容，由于lsb_num为1，仅替换第八位
        carrier_bits[i * scope_num:, 8 - num_lsb:8] = payload_bits.reshape(bit_height, num_lsb)
        ret = np.packbits(carrier_bits).tobytes()
        carrier = ret + carrier[(bit_height + i * scope_num)*2:]
    return carrier


# 增强鲁棒性，通过判断音频文件位数进行指定位置添加隐写内容,规则可自行修改（并非每一秒都添加）
def set_scope_num(max_bytes_to_hide):
    scope_num = max_bytes_to_hide
    if int(max_bytes_to_hide) > 500000:
        scope_num = 500
    if int(max_bytes_to_hide) > 5000000:
        scope_num = 5000
    elif int(max_bytes_to_hide) > 10000000:
        scope_num = 50000
    elif int(max_bytes_to_hide) > 20000000:
        scope_num = 50000
    return scope_num


# 解析音频数据
def lsb_deinterleave_bytes(carrier, num_bits, num_lsb, byte_depth=1):
    plen = roundup(num_bits / num_lsb)
    carrier_dtype = byte_depth_to_dtype[byte_depth]
    payload_bits = np.unpackbits(
        np.frombuffer(carrier, dtype=carrier_dtype, count=plen).view(np.uint8)
    ).reshape(plen, 8 * byte_depth)[:, 8 - num_lsb : 8]
    return np.packbits(payload_bits).tobytes()[: num_bits // 8]
