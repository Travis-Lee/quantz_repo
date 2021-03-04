from decimal import Decimal


def round_half_up(num):
    '''
    四舍五入,保留小数点后3位
    '''
    return Decimal(num).quantize(Decimal('0.001'), rounding="ROUND_HALF_UP")
