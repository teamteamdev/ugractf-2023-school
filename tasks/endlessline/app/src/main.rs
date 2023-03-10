#[macro_use] extern crate rocket;
use rocket_dyn_templates::{Template, context};
use rocket::http::CookieJar;
use rocket::http::Cookie;
use rand::Rng;
use chrono::TimeZone;
use crc32fast::Hasher;
use sha2::{Sha256, Digest};

const COOKIE_NAME: &str = "status";

const FLAG_PREFIX: &str = "ugra_spasibo_za_ozhidaniye_";
const FLAG_SEED: &str = "helloWORLDthisISaSUPERsecureSECRETseed"; // CHANGEME
const SUFFIX_LENGTH: usize = 12;

// Define error types
enum ErrorType {
  HashMismatch,
  NegativeQueuePos,
  FutureUpdatedTime,
}

fn gen_flag(token: String) -> String {
  // This function in python:
  // return PREFIX + hmac.new(SECRET, token.encode(), "sha256").hexdigest()[:SUFFIX_SIZE]

  let mut hasher = Sha256::new();
  // Use the seed as the key and the token as the message
  hasher.update(FLAG_SEED.as_bytes());
  hasher.update(token.as_bytes());
  let result = hasher.finalize();
  let result = format!("{:x}", result);

  format!("{}{}", FLAG_PREFIX, &result[..SUFFIX_LENGTH])
}

fn get_queue_position() -> i32 {
  // Generate a random number between 30 and 100
  rand::thread_rng().gen_range(30..100)
}

fn get_time_to_wait(pos: i32) -> i32 {
  // Generate a random number between 5 and 50 and multiply it by the queue position
  pos * rand::thread_rng().gen_range(5..50)
}

fn update_cookies(cookies: &CookieJar<'_>, queue_pos: i32, time_to_wait: i32) -> String {
  let mut hasher = Hasher::new();
  let hash;
  let time_updated = chrono::Utc::now().to_string();

  // Hash the cookie data
  let cookie_data = format!("{},{},{}", queue_pos, time_to_wait, time_updated);
  hasher.update(&cookie_data.as_bytes());
  hash = hasher.finalize();
  
  // Write the cookie data to a string including the hash
  let cookie_data = format!("{},{},{},{}", queue_pos, time_to_wait, time_updated, hash);

  // Set the cookie
  cookies.add(Cookie::new(COOKIE_NAME, cookie_data));

  // Return the time updated
  time_updated
}

fn update_times<'a>(cookies: &'a CookieJar<'a>, time_updated: String, mut queue_pos: i32, mut time_to_wait: i32) -> (i32, i32, &'a str) {
  // Update the time to wait if it's been more than 1 minute since the last update
  // Remove "UTC" from the end of the string
  let time_updated = time_updated.trim_end_matches(" UTC");

  let time_updated = chrono::Utc.datetime_from_str(&time_updated, "%Y-%m-%d %H:%M:%S%.f").unwrap();
  let time_now = chrono::Utc::now();
  let time_diff = time_now.signed_duration_since(time_updated);


  if time_diff.num_minutes() >= 1 {
    // If at least 1 minute has passed, update the time to wait
    // Substract the time that has passed since the last update
    time_to_wait -= time_diff.num_minutes() as i32;
  } else if time_diff.num_minutes() < 0 {
    // If the time updated is in the future, return an error
    return (queue_pos, time_to_wait, gen_error_text(ErrorType::FutureUpdatedTime));
  } else {
    // If not, move the user 1 place down in the queue and update the time to wait
    queue_pos += 1;
    time_to_wait += get_time_to_wait(1);
  } 

  // Update the cookies
  update_cookies(cookies, queue_pos, time_to_wait);

  (queue_pos, time_to_wait, "")
}

fn gen_error_text(error: ErrorType) -> &'static str {
  // Pick a random response from the array
  let hash_mismatch_responces = [
    "Ошибка проверки цифровой подписи. Этот инцидент будет зарегистрирован. Системный администратор уже в пути к вам.",
    "Не удалось сверить счета. Бухгалтерия уже занимается вашим делом.",
    "Где-то что-то сломалось. Кто-то уже как-то что-то делает.",
    "У нас проблемы. Наш отряд ДевоПсов уже работает над этим.",
    "Кажется, кто-то пытается нас взломать. Наряд хакеров уже в пути.",
    "Блин да как так-то???",
  ];
  
  let negative_queue_pos_responces = [
    "Замечен разрыв непрерывном полотне очереди. Ближайший математик оповещен.",
    "Кто-то пытался взять вас за хвост. Но мы его заметили и убрали. Пожалуйста заберите свой хвост в кабинете номер 502.",
    "Вы пропустили свой номер. Пожалуйста, возьмите новый.",
    "Ваша очередь уже не наступила. Пожалуйста, подождите.",
    "Наша очередь работает только в одну сторону. Пожалуйста, вернитесь назад.",
    "Ёжик съел ваш номер. Пожалуйста, попросите его вернуть его.",
    "how???",
    "Извините, у нас со своими минусами нельзя.",
    "Вы оказались недостаточно 🚀 blazing fast 🚀, и пропустили своё место в очереди.",
  ];

  let future_updated_time_responces = [
    "Обнаружен разрыв пространства-времени. Ваше время еще не наступило. Пожалуйста, подождите.",
    "Кажется, сервер совершил прыжок во времени. Пожалуйста, подождите, пока он вернется.",
    "Пожалуйста, проверьте свою кукушку. Кажется, ей нужна замена батареек.",
    "Извините, мы не обслуживаем путешественников во времени. Пожалуйста, вернитесь в прошлое.",
    "Йоу, ты из будущего? Ну тогда поздравляю, ты первый.",
    "У вас хлеб прошлогодний.",
    "Кажется, вы забыли выключить машину времени.",
    "Наш сервер не настолько 🚀 blazing fast 🚀 чтобы обрабатывать запросы из будущего.",
  ];


  match error {
    ErrorType::HashMismatch => {
      let random_index = rand::thread_rng().gen_range(0..hash_mismatch_responces.len());
      hash_mismatch_responces[random_index]
    },
    ErrorType::NegativeQueuePos => {
      let random_index = rand::thread_rng().gen_range(0..negative_queue_pos_responces.len());
      negative_queue_pos_responces[random_index]
    },
    ErrorType::FutureUpdatedTime => {
      let random_index = rand::thread_rng().gen_range(0..future_updated_time_responces.len());
      future_updated_time_responces[random_index]
    },
  }
}

#[get("/<token>")]
fn index(cookies: &CookieJar<'_> , token: String) -> Template {
  let queue_pos: i32;
  let time_to_wait:i32;
  let time_updated;
  let cookie_data;
  let mut hasher = Hasher::new();
  let hash;
  let error_text;

  println!("flag: {}", gen_flag(token.clone()));

  if cookies.get(COOKIE_NAME).is_none() {
    // If the cookies don't exist, generate them
    queue_pos = get_queue_position();
    time_to_wait = get_time_to_wait(queue_pos);
    
    time_updated = update_cookies(cookies, queue_pos, time_to_wait);
    
  } else {
    // If the cookie exists, get the data from it
    cookie_data = cookies.get(COOKIE_NAME).unwrap().value().to_string();

    // Split the cookie data into an array
    let mut cookie_data: Vec<&str> = cookie_data.split(",").collect();

    // Get the hash from the cookie data and remove it from the array
    hash = cookie_data[3].parse::<u32>().unwrap();
    cookie_data.pop();

    // Compare the hash with the hash of the cookie data
    hasher.update(&cookie_data.join(",").as_bytes());
    if hasher.finalize() != hash {
      // If the hashes don't match, delete the cookie and redirect to the index page
      println!("Hashes don't match! Deleting cookie... ");
      error_text = gen_error_text(ErrorType::HashMismatch);
      cookies.remove(Cookie::named(COOKIE_NAME));

      queue_pos = get_queue_position();
      time_to_wait = get_time_to_wait(queue_pos);

      update_cookies(cookies, queue_pos, time_to_wait);

      return Template::render("index", context! {
        queue_position: queue_pos,
        time_to_wait: time_to_wait,
        error_text: error_text,
      })
    }

    // Get the queue position, time to wait and time updated from the cookie data
    queue_pos = cookie_data[0].parse::<i32>().unwrap();
    time_to_wait = cookie_data[1].parse::<i32>().unwrap();
    time_updated = cookie_data[2].to_string();
  }

  if queue_pos < 0 {
    error_text = gen_error_text(ErrorType::NegativeQueuePos);

    return Template::render("index", context! {
      queue_position: queue_pos,
      time_to_wait: time_to_wait,
      error_text: error_text,
    })
  }

  if time_to_wait < 0 {
    error_text = gen_error_text(ErrorType::FutureUpdatedTime);

    return Template::render("index", context! {
      queue_position: queue_pos,
      time_to_wait: time_to_wait,
      error_text: error_text,
    })
  }

  // Update the queue position and time to wait
  let (queue_pos, time_to_wait, error_text) = update_times(cookies, time_updated, queue_pos, time_to_wait);


  // Render the template
  if queue_pos == 0 {
    return Template::render("success", context! {
      flag: gen_flag(token)
    })
  } else {
    Template::render("index", context! {
      queue_position: queue_pos,
      time_to_wait: time_to_wait,
      error_text: error_text,
    })
  }
}

#[launch]
fn rocket() -> _ {
  rocket::build().attach(Template::fairing())
    .mount("/", routes![index])
}