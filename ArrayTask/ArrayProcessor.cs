using System;
using System.Collections.Generic;
using System.Numerics;

namespace ArrayTask;

public static class ArrayProcessor
{
    public static (double[] Elements, BigInteger Sum) FindByDigit(
        double[] numbers, int digit)
    {
        if (numbers == null)
        {
            throw new ArgumentNullException(nameof(numbers));
        }

        if (digit < 0 || digit > 9)
        {
            throw new ArgumentOutOfRangeException(
                nameof(digit), "Цифра должна быть от 0 до 9.");
        }

        List<double> elements = new List<double>();
        BigInteger sum = BigInteger.Zero;

        foreach (double number in numbers)
        {
            if (!double.IsFinite(number))
            {
                throw new ArgumentException(
                    "Элементы массива должны быть конечными числами.",
                    nameof(numbers));
            }

            BigInteger integerPart = new BigInteger(number);
            BigInteger remainingDigits = BigInteger.Abs(integerPart);
            bool containsDigit = false;

            do
            {
                if (remainingDigits % 10 == digit)
                {
                    containsDigit = true;
                    break;
                }

                remainingDigits /= 10;
            }
            while (remainingDigits > 0);

            if (containsDigit)
            {
                elements.Add(number);
                sum += integerPart;
            }
        }

        return (elements.ToArray(), sum);
    }
}
