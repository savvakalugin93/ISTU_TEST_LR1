using System;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Numerics;
using System.Text.Json;

namespace ArrayTask.Tests;

internal static class TestProtocol
{
    public static void SaveSuccess(string testName, double[] elements, BigInteger sum)
    {
        Save(testName, new
        {
            elements = elements.Select(x => x.ToString("R", CultureInfo.InvariantCulture)).ToArray(),
            sum = sum.ToString(CultureInfo.InvariantCulture)
        });
    }

    public static void SaveError(string testName, ArgumentException error)
    {
        Save(testName, new
        {
            error = error.GetType().Name,
            parameter = error.ParamName
        });
    }

    private static void Save(string testName, object result)
    {
        string folder = Environment.GetEnvironmentVariable("LR1_PROTOCOL_DIR")
            ?? Path.Combine(AppContext.BaseDirectory, "actual-results");

        Directory.CreateDirectory(folder);
        string path = Path.Combine(folder, testName + ".json");
        File.WriteAllText(path, JsonSerializer.Serialize(result));
    }
}
