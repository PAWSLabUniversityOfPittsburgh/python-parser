
// enter code here
public class JArrayMax {

  public static void main(String[] args) {

    int[] values = {5, 8, 4, 78, 95, 12, 1, 0, 6, 35, 46};

    int maxValue = values[0];

    for (int i = 1; i < values.length; i++) {

      if (values[i] > maxValue) {

        maxValue = values[i];

      }

    }

    System.out.println("Maximum value: " + maxValue);

  }

}